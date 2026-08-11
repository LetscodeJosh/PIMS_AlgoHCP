/**
 * Risk-Based HCP Identity Resolution System (JavaScript / Node / Browser Engine)
 * ==============================================================================
 * Guiding Principle:
 * Favor preserving separate records over incorrectly merging two distinct physicians.
 * Duplicate records can be merged later after additional evidence is available, whereas
 * an incorrect merge compromises HCP history, reporting, and engagement records and
 * is significantly more difficult to reverse.
 */

const ConfidenceTier = {
    HIGH: "HIGH",
    MEDIUM: "MEDIUM",
    LOW: "LOW"
};

const ActionTier = {
    MERGE: "MERGE",
    MANUAL_REVIEW: "MANUAL_REVIEW",
    KEEP_SEPARATE: "KEEP_SEPARATE"
};

const StewardDecision = {
    PENDING: "PENDING",
    APPROVED_MERGE: "APPROVED_MERGE",
    REJECTED_SEPARATE: "REJECTED_SEPARATE",
    DEFERRED: "DEFERRED"
};

class NameStandardizer {
    static stripAccents(str) {
        return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    static standardizeName(name) {
        if (!name) return "";
        let cleaned = this.stripAccents(name).toLowerCase();

        // Strip titles & suffixes
        const titles = [
            /\bdr\b\.?/gi, /\bdra\b\.?/gi, /\bdoctor\b/gi, /\bdoctora\b/gi, /\bprof\b\.?/gi,
            /\bmd\b\.?/gi, /\bfpoa\b\.?/gi, /\bfpcp\b\.?/gi, /\bfpcs\b\.?/gi, /\bdpbr\b\.?/gi
        ];
        titles.forEach(t => { cleaned = cleaned.replace(t, ""); });

        // Expand abbreviations
        cleaned = cleaned.replace(/\bma\b\.?/gi, "maria");
        cleaned = cleaned.replace(/\bst\b\.?/gi, "saint");
        cleaned = cleaned.replace(/\bsta\b\.?/gi, "santa");
        cleaned = cleaned.replace(/\bdela\b/gi, "de la");

        // Remove non-alphanumeric except spaces
        cleaned = cleaned.replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
        return cleaned;
    }

    static getTokenSortedKey(name) {
        const std = this.standardizeName(name);
        return std.split(" ").sort().join(" ");
    }
}

class SimilarityMetrics {
    static jaroWinkler(s1, s2, p = 0.1) {
        if (s1 === s2) return 1.0;
        if (!s1 || !s2) return 0.0;

        const len1 = s1.length;
        const len2 = s2.length;
        const matchDistance = Math.max(0, Math.floor(Math.max(len1, len2) / 2) - 1);

        const s1Matches = new Array(len1).fill(false);
        const s2Matches = new Array(len2).fill(false);

        let matches = 0;
        let transpositions = 0;

        for (let i = 0; i < len1; i++) {
            const start = Math.max(0, i - matchDistance);
            const end = Math.min(i + matchDistance + 1, len2);
            for (let j = start; j < end; j++) {
                if (s2Matches[j]) continue;
                if (s1[i] === s2[j]) {
                    s1Matches[i] = true;
                    s2Matches[j] = true;
                    matches++;
                    break;
                }
            }
        }

        if (matches === 0) return 0.0;

        let k = 0;
        for (let i = 0; i < len1; i++) {
            if (!s1Matches[i]) continue;
            while (!s2Matches[k]) k++;
            if (s1[i] !== s2[k]) transpositions++;
            k++;
        }

        const jaro = (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3.0;

        let prefixLen = 0;
        for (let i = 0; i < Math.min(4, Math.min(len1, len2)); i++) {
            if (s1[i] === s2[i]) prefixLen++;
            else break;
        }

        return jaro + prefixLen * p * (1.0 - jaro);
    }

    static tokenSetSimilarity(s1, s2) {
        if (!s1 || !s2) return 0.0;
        const set1 = new Set(s1.toLowerCase().trim().split(/\s+/));
        const set2 = new Set(s2.toLowerCase().trim().split(/\s+/));

        let intersection = 0;
        set1.forEach(val => { if (set2.has(val)) intersection++; });
        const union = new Set([...set1, ...set2]).size;

        return union === 0 ? 0.0 : intersection / union;
    }
}

class HCPMatcher {
    constructor(config = {}) {
        this.wName = config.wName ?? 0.40;
        this.wSpecialty = config.wSpecialty ?? 0.20;
        this.wInstitution = config.wInstitution ?? 0.20;
        this.wLocation = config.wLocation ?? 0.10;
        this.wHistory = config.wHistory ?? 0.10;

        this.highThreshold = config.highThreshold ?? 0.85;
        this.mediumThreshold = config.mediumThreshold ?? 0.60;
    }

    evaluatePair(recA, recB) {
        const stdA = NameStandardizer.standardizeName(recA.full_name);
        const stdB = NameStandardizer.standardizeName(recB.full_name);

        const jw = SimilarityMetrics.jaroWinkler(stdA, stdB);
        const tokenJw = SimilarityMetrics.jaroWinkler(
            NameStandardizer.getTokenSortedKey(recA.full_name),
            NameStandardizer.getTokenSortedKey(recB.full_name)
        );
        const sName = Math.max(jw, tokenJw);

        const sSpec = SimilarityMetrics.tokenSetSimilarity(recA.specialty || "", recB.specialty || "");
        
        let sInst = 0.0;
        if (recA.institution_id && recB.institution_id && recA.institution_id === recB.institution_id) {
            sInst = 1.0;
        } else if (recA.institution_name && recB.institution_name) {
            sInst = SimilarityMetrics.tokenSetSimilarity(recA.institution_name, recB.institution_name);
        }

        let sLoc = 0.0;
        let locEvals = 0;
        let locMatches = 0;
        if (recA.city && recB.city) {
            locEvals++;
            if (recA.city.toLowerCase().trim() === recB.city.toLowerCase().trim()) locMatches++;
        }
        if (recA.province && recB.province) {
            locEvals++;
            if (recA.province.toLowerCase().trim() === recB.province.toLowerCase().trim()) locMatches++;
        }
        if (locEvals > 0) sLoc = locMatches / locEvals;

        let sHist = 0.0;
        if (recA.email && recB.email && recA.email.toLowerCase().trim() === recB.email.toLowerCase().trim()) {
            sHist = 1.0;
        }

        const totalScore = (
            this.wName * sName +
            this.wSpecialty * sSpec +
            this.wInstitution * sInst +
            this.wLocation * sLoc +
            this.wHistory * sHist
        );

        // Corroboration rule requirement
        const isCorroborated = (sInst >= 0.80 || sSpec >= 0.90 || sLoc >= 0.85 || sHist >= 0.90);

        let confidenceTier, recommendedAction, explanation;

        if (totalScore >= this.highThreshold) {
            if (isCorroborated) {
                confidenceTier = ConfidenceTier.HIGH;
                recommendedAction = ActionTier.MERGE;
                explanation = `High confidence (${(totalScore * 100).toFixed(1)}%): Name match corroborated by supporting attributes. Safe auto-merge.`;
            } else {
                confidenceTier = ConfidenceTier.MEDIUM;
                recommendedAction = ActionTier.MANUAL_REVIEW;
                explanation = `Medium confidence (${(totalScore * 100).toFixed(1)}%): High name match lacks corroborating supporting evidence. Flagged for Data Steward review to prevent false merge.`;
            }
        } else if (totalScore >= this.mediumThreshold) {
            confidenceTier = ConfidenceTier.MEDIUM;
            recommendedAction = ActionTier.MANUAL_REVIEW;
            explanation = `Medium confidence (${(totalScore * 100).toFixed(1)}%): Partial attribute match. Flagged for Data Steward review.`;
        } else {
            confidenceTier = ConfidenceTier.LOW;
            recommendedAction = ActionTier.KEEP_SEPARATE;
            explanation = `Low confidence (${(totalScore * 100).toFixed(1)}%): Insufficient attribute match. Records preserved separately.`;
        }

        return {
            candidate_a_id: recA.id,
            candidate_b_id: recB.id,
            name_score: sName,
            specialty_score: sSpec,
            institution_score: sInst,
            location_score: sLoc,
            history_score: sHist,
            total_score: totalScore,
            is_corroborated: isCorroborated,
            confidence_tier: confidenceTier,
            recommended_action: recommendedAction,
            explanation: explanation
        };
    }
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        ConfidenceTier,
        ActionTier,
        StewardDecision,
        NameStandardizer,
        SimilarityMetrics,
        HCPMatcher
    };
}
