/**
 * PIMS_AlgoHCP Client Application Logic
 * Supports New Doctor Canonical Verification & Automatic Master Dictionary Commit
 */

const API_BASE = window.location.origin + "/api";

let currentMatches = [];
let pendingReviews = [];
let dictionaryData = [];
let masterlistData = [];
let autoDetectDebounceTimer = null;

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  loadMasterlist();
  loadDictionary();
  loadReviews();

  document.querySelectorAll(".auto-detect-field").forEach(input => {
    input.addEventListener("keyup", () => {
      input.style.borderColor = "";
      triggerAutoDetect();
    });
    input.addEventListener("change", () => {
      input.style.borderColor = "";
      triggerAutoDetect();
    });
  });

  document.getElementById("btn-check-recognizer").addEventListener("click", runRecognizerCheck);
  document.getElementById("btn-submit-entry").addEventListener("click", submitMedRepEntry);
  document.getElementById("btn-run-workbench").addEventListener("click", runWorkbenchTest);
  
  document.getElementById("warning-modal-close").addEventListener("click", closeWarningModal);
  document.getElementById("warning-modal-btn").addEventListener("click", closeWarningModal);

  document.getElementById("modal-close-btn").addEventListener("click", closeModal);
  document.getElementById("modal-cancel-btn").addEventListener("click", closeModal);
  document.getElementById("dict-modal-close").addEventListener("click", () => {
    document.getElementById("dict-modal-backdrop").classList.remove("active");
  });

  triggerAutoDetect();
});

// Tab Switching
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "tab-reviews") loadReviews();
      if (targetId === "tab-masterlist") loadMasterlist();
      if (targetId === "tab-dictionary") loadDictionary();
    });
  });
}

function switchTab(tabId) {
  const tabBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  if (tabBtn) {
    tabBtn.click();
  }
}

function loadPreset(name, spec, hosp, secHosp, addr, city, contact, email) {
  document.getElementById("input-doc-name").value = name;
  document.getElementById("input-doc-spec").value = spec;
  document.getElementById("input-doc-hosp").value = hosp;
  document.getElementById("input-doc-sec-hosp").value = secHosp;
  document.getElementById("input-doc-address").value = addr;
  document.getElementById("input-doc-city").value = city;
  document.getElementById("input-doc-contact").value = contact;
  document.getElementById("input-doc-email").value = email;

  document.querySelectorAll(".auto-detect-field").forEach(inp => inp.style.borderColor = "");
  triggerAutoDetect();
}

function triggerAutoDetect() {
  clearTimeout(autoDetectDebounceTimer);
  autoDetectDebounceTimer = setTimeout(runAutoDetectScan, 300);
}

async function runAutoDetectScan() {
  const candidate = getMedRepInput();
  const bannerTitle = document.getElementById("banner-title");
  const bannerDesc = document.getElementById("banner-desc");
  const bannerBadge = document.getElementById("banner-badge");

  if (!candidate.name || candidate.name.trim().length < 3) {
    bannerTitle.textContent = "Intelligent Pre-Submission Recognizer Active";
    bannerDesc.textContent = "Fill out all mandatory doctor fields to scan master records automatically...";
    bannerBadge.innerHTML = `<span class="badge" style="background:rgba(255,255,255,0.1); color:var(--text-muted)">Mandatory Validation</span>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate })
    });
    const data = await res.json();
    if (data.status === "success" && data.matches.length > 0) {
      currentMatches = data.matches;
      const top = currentMatches[0];

      bannerTitle.innerHTML = `⚡ Real-Time Intelligent Detection: <strong>${top.confidence_pct}% Match</strong> with <u>${top.master_record.name}</u>`;
      bannerDesc.textContent = `Master Profile ID: ${top.master_id} | ${top.master_record.hospital} | ${top.master_record.specialty}`;

      bannerBadge.innerHTML = `
        <span class="badge" style="background:${top.badge_color}22; color:${top.badge_color}; border:1px solid ${top.badge_color}">
          ${top.tier}
        </span>
      `;
    }
  } catch (e) {
    console.error("Auto detect scan error:", e);
  }
}

function getMedRepInput() {
  return {
    medrep_name: document.getElementById("medrep-user-name").value.trim() || "MedRep User",
    name: document.getElementById("input-doc-name").value.trim(),
    specialty: document.getElementById("input-doc-spec").value.trim(),
    hospital: document.getElementById("input-doc-hosp").value.trim(),
    secondary_hospital: document.getElementById("input-doc-sec-hosp").value.trim(),
    address: document.getElementById("input-doc-address").value.trim(),
    city: document.getElementById("input-doc-city").value.trim(),
    contact: document.getElementById("input-doc-contact").value.trim(),
    email: document.getElementById("input-doc-email").value.trim()
  };
}

function validateMandatoryInput(candidate) {
  const missing = [];
  const fieldsToCheck = [
    { key: "name", id: "input-doc-name", label: "Doctor Full Name" },
    { key: "specialty", id: "input-doc-spec", label: "Specialty" },
    { key: "hospital", id: "input-doc-hosp", label: "Primary Hospital / Institution" },
    { key: "secondary_hospital", id: "input-doc-sec-hosp", label: "Secondary Hospital / Clinic" },
    { key: "address", id: "input-doc-address", label: "Street / Barangay Address" },
    { key: "city", id: "input-doc-city", label: "City / Municipality" },
    { key: "contact", id: "input-doc-contact", label: "Contact Number" },
    { key: "email", id: "input-doc-email", label: "Email Address" }
  ];

  fieldsToCheck.forEach(f => {
    const elem = document.getElementById(f.id);
    if (!candidate[f.key] || candidate[f.key].length === 0) {
      missing.push(f.label);
      if (elem) elem.style.borderColor = "#EF4444";
    } else {
      if (elem) elem.style.borderColor = "";
    }
  });

  return missing;
}

function showWarningModal(missingFields) {
  const backdrop = document.getElementById("warning-modal-backdrop");
  const listElem = document.getElementById("warning-missing-list");
  listElem.innerHTML = missingFields.map(f => `<li><strong>${f}</strong></li>`).join("");
  backdrop.classList.add("active");
}

function closeWarningModal() {
  document.getElementById("warning-modal-backdrop").classList.remove("active");
}

function resetFormInput() {
  document.getElementById("input-doc-name").value = "";
  document.getElementById("input-doc-spec").value = "";
  document.getElementById("input-doc-hosp").value = "";
  document.getElementById("input-doc-sec-hosp").value = "";
  document.getElementById("input-doc-address").value = "";
  document.getElementById("input-doc-city").value = "";
  document.getElementById("input-doc-contact").value = "";
  document.getElementById("input-doc-email").value = "";
  
  document.querySelectorAll(".auto-detect-field").forEach(inp => inp.style.borderColor = "");
  triggerAutoDetect();
}

async function loadMasterlist() {
  try {
    const res = await fetch(`${API_BASE}/masterlist`);
    const data = await res.json();
    if (data.status === "success") {
      masterlistData = data.masterlist;
      renderMasterlist(masterlistData);
    }
  } catch (e) {
    console.error("Error loading masterlist:", e);
  }
}

function renderMasterlist(records) {
  const tbody = document.getElementById("masterlist-tbody");
  if (!tbody) return;
  tbody.innerHTML = records.map(r => {
    let statusBadge = `<span class="badge" style="background:rgba(14, 165, 233, 0.15); color:var(--primary);">VERIFIED</span>`;
    if (r.status === "PENDING_MANAGERIAL_VERIFICATION") {
      statusBadge = `<span class="badge" style="background:rgba(245, 158, 11, 0.2); color:#F59E0B;">PENDING MANAGER VERIFICATION</span>`;
    } else if (r.status === "VERIFIED_LOCKED") {
      statusBadge = `<span class="badge" style="background:rgba(16, 185, 129, 0.2); color:#10B981;">🔒 VERIFIED & IMMUTABLE</span>`;
    }

    return `
      <tr>
        <td><strong>${r.id}</strong><br>${statusBadge}</td>
        <td><strong>${r.name}</strong><br><small style="color:var(--text-dim)">Canonical: ${r.canonical_name}</small></td>
        <td><span class="badge" style="background:rgba(14, 165, 233, 0.15); color:var(--primary);">${r.specialty}</span></td>
        <td>${r.hospital}</td>
        <td>${r.city}, ${r.province || ''}</td>
        <td>${r.contact || 'N/A'}</td>
      </tr>
    `;
  }).join("");
}

async function loadDictionary() {
  try {
    const res = await fetch(`${API_BASE}/dictionary`);
    const data = await res.json();
    if (data.status === "success") {
      dictionaryData = data.dictionary;
      renderDictionary(dictionaryData);
    }
  } catch (e) {
    console.error("Error loading dictionary:", e);
  }
}

function renderDictionary(records) {
  const tbody = document.getElementById("dictionary-tbody");
  if (!tbody) return;
  tbody.innerHTML = records.map(d => `
    <tr>
      <td><span class="badge" style="background:rgba(16, 185, 129, 0.2); color:#10B981;">100% VERIFIED CANONICAL</span><br><strong>${d.id}</strong></td>
      <td><strong>${d.name}</strong><br><small style="color:var(--text-muted)">${d.full_canonical_name}</small></td>
      <td><strong>${d.specialty}</strong></td>
      <td><strong>Primary:</strong> ${d.primary_hospital}<br><small style="color:var(--text-muted)">Secondary: ${d.secondary_hospital}</small></td>
      <td>${d.city}, ${d.province}</td>
      <td><small>${d.dictionary_notes}</small></td>
    </tr>
  `).join("");
}

async function loadReviews() {
  try {
    const res = await fetch(`${API_BASE}/reviews`);
    const data = await res.json();
    if (data.status === "success") {
      pendingReviews = data.reviews;
      renderReviews(pendingReviews);
      document.getElementById("review-badge-count").textContent = pendingReviews.length;
    }
  } catch (e) {
    console.error("Error loading reviews:", e);
  }
}

function renderReviews(reviews) {
  const container = document.getElementById("reviews-container");
  if (!container) return;

  if (reviews.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align:center; padding:3rem;">
        <h3 style="color:var(--text-muted)">No Pending Managerial Reviews</h3>
        <p style="color:var(--text-dim); margin-top:0.5rem;">All submissions and new doctor verification requests have been processed.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = reviews.map(rev => {
    const top = rev.top_match;
    const cand = rev.candidate;
    const mast = top ? top.master_record : {};
    const isNewDoctorVerification = rev.review_type === "NEW_DOCTOR_VERIFICATION";
    
    return `
      <div class="card" style="margin-bottom:1.5rem; border:1px solid ${top ? top.badge_color : 'var(--border-color)'}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; border-bottom:1px solid var(--border-color); padding-bottom:0.75rem;">
          <div>
            <span class="badge" style="background:rgba(245,158,11,0.2); color:#F59E0B; margin-right:0.5rem;">${rev.review_id}</span>
            <span class="badge" style="background:rgba(14, 165, 233, 0.2); color:var(--primary);">${rev.current_stage}</span>
            ${isNewDoctorVerification ? `<span class="badge" style="background:rgba(139,92,246,0.2); color:#8B5CF6; margin-left:0.5rem;">NEW DOCTOR VERIFICATION</span>` : ''}
          </div>
          <div style="text-align:right">
            <span style="font-size:1.4rem; font-weight:800; color:${top ? top.badge_color : '#FFF'}">${rev.confidence_pct}% Match</span>
            <div style="font-size:0.75rem; color:var(--text-dim)">Submitted: ${rev.submission_date} by ${rev.medrep_name}</div>
          </div>
        </div>

        <div style="margin-bottom:1rem;">
          <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.5rem;">
            ${isNewDoctorVerification ? 'New Doctor Profile Details (Verify Canonical Data)' : 'Multi-Field Comparison Matrix'}
          </h4>
          <div class="comparison-container">
            <div class="comp-box">
              <h4>Submitted Doctor Info (MedRep Entry)</h4>
              <div class="field-pair"><div class="label">Doctor Full Name</div><div class="val" style="color:#0EA5E9">${cand.name}</div></div>
              <div class="field-pair"><div class="label">Specialty</div><div class="val">${cand.specialty}</div></div>
              <div class="field-pair"><div class="label">Primary Hospital</div><div class="val">${cand.hospital}</div></div>
              <div class="field-pair"><div class="label">Secondary Clinic</div><div class="val">${cand.secondary_hospital || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Street Address</div><div class="val">${cand.address || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">City / Municipality</div><div class="val">${cand.city}</div></div>
              <div class="field-pair"><div class="label">Contact / Email</div><div class="val">${cand.contact || 'N/A'} | ${cand.email || 'N/A'}</div></div>
            </div>

            <div class="comp-box highlight">
              <h4>${isNewDoctorVerification ? 'Pending Master Profile' : 'Candidate Masterlist Record (' + (mast.id || 'N/A') + ')'}</h4>
              <div class="field-pair"><div class="label">Master ID</div><div class="val" style="color:#10B981">${mast.id || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Doctor Name</div><div class="val" style="color:#10B981">${mast.name || cand.name}</div></div>
              <div class="field-pair"><div class="label">Specialty</div><div class="val">${mast.specialty || cand.specialty}</div></div>
              <div class="field-pair"><div class="label">Primary Hospital</div><div class="val">${mast.hospital || cand.hospital}</div></div>
              <div class="field-pair"><div class="label">City</div><div class="val">${mast.city || cand.city}</div></div>
              <div class="field-pair"><div class="label">Status</div><div class="val" style="color:#F59E0B">${isNewDoctorVerification ? 'Pending Managerial Verification' : 'Verified'}</div></div>
            </div>
          </div>
        </div>

        <div style="background:rgba(15, 23, 42, 0.8); padding:0.75rem 1rem; border-radius:var(--radius-md); margin-bottom:1rem; font-size:0.82rem;">
          <strong>Escalation & Verification Audit Log:</strong>
          <ul style="margin-left:1.2rem; margin-top:0.3rem; color:var(--text-muted)">
            ${rev.escalation_history.map(h => `<li><strong>[${h.timestamp}] ${h.actor}:</strong> ${h.note}</li>`).join("")}
          </ul>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
          <button class="btn btn-secondary" onclick="openDictionaryModal('${cand.name}')">
            📖 Consult Verified Dictionary (100% Correct Baseline)
          </button>
          <div style="display:flex; gap:0.5rem">
            ${rev.assigned_level < 2 ? `
              <button class="btn btn-warning" onclick="escalateReview('${rev.review_id}')">
                ⬆️ Pass to Higher Position (Escalate)
              </button>
            ` : ''}
            
            ${isNewDoctorVerification ? `
              <button class="btn btn-success" style="background:linear-gradient(135deg, #10B981 0%, #059669 100%);" onclick="resolveReview('${rev.review_id}', 'VERIFY_AND_LOCK_CANONICAL', '${mast.id}')">
                🔒 Verify & Lock Canonical Info (Commit to 100% Dictionary)
              </button>
            ` : `
              <button class="btn btn-secondary" onclick="resolveReview('${rev.review_id}', 'KEEP_SEPARATE', '${mast.id}')">
                ❌ Keep Separate Records
              </button>
              <button class="btn btn-success" onclick="resolveReview('${rev.review_id}', 'MERGE_RECORD', '${mast.id}')">
                ✅ Approve & Merge HCP Profile
              </button>
            `}
          </div>
        </div>
      </div>
    `;
  }).join("");
}

async function runRecognizerCheck() {
  const candidate = getMedRepInput();
  const missing = validateMandatoryInput(candidate);

  if (missing.length > 0) {
    showWarningModal(missing);
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate })
    });
    const data = await res.json();
    if (data.status === "success") {
      currentMatches = data.matches;
      openRecognizerModal(candidate, currentMatches);
    }
  } catch (e) {
    console.error("Recognizer error:", e);
  }
}

function openRecognizerModal(candidate, matches) {
  const backdrop = document.getElementById("modal-backdrop");
  const modalBody = document.getElementById("modal-body-content");

  modalBody.innerHTML = `
    <div style="background:rgba(14, 165, 233, 0.1); border:1px solid var(--border-glow); padding:1rem; border-radius:var(--radius-md); margin-bottom:1.25rem;">
      <h4 style="color:var(--primary); font-size:0.9rem; text-transform:uppercase; margin-bottom:0.25rem;">Submitted Candidate Input</h4>
      <div style="font-size:1.1rem; font-weight:700;">${candidate.name}</div>
      <div style="font-size:0.85rem; color:var(--text-muted);">${candidate.specialty} | ${candidate.hospital} | ${candidate.city}</div>
    </div>

    <h4 style="font-size:0.95rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.75rem;">
      Algorithm Recognizer Matches (${matches.length} Master Candidates Found)
    </h4>

    ${matches.map(m => `
      <div class="match-candidate-item">
        <div class="candidate-top">
          <div>
            <span class="candidate-name">${m.master_record.name}</span>
            <small style="margin-left:0.5rem; color:var(--text-dim)">ID: ${m.master_id}</small>
          </div>
          <div>
            <span class="badge" style="background:${m.badge_color}22; color:${m.badge_color}; border:1px solid ${m.badge_color}">
              ${m.confidence_pct}% Match (${m.tier})
            </span>
          </div>
        </div>

        <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">
          <strong>Hospital:</strong> ${m.master_record.hospital} | <strong>Specialty:</strong> ${m.master_record.specialty} | <strong>City:</strong> ${m.master_record.city}
        </div>

        <div style="background:rgba(0,0,0,0.3); padding:0.8rem; border-radius:var(--radius-sm); font-size:0.78rem;">
          <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.5rem; margin-bottom:0.5rem;">
            <div>Name Match: <strong>${m.breakdown.name.score}%</strong> (${m.breakdown.name.status})</div>
            <div>Specialty: <strong>${m.breakdown.specialty.score}%</strong> (${m.breakdown.specialty.status})</div>
            <div>Hospital: <strong>${m.breakdown.hospital.score}%</strong> (${m.breakdown.hospital.status})</div>
            <div>City: <strong>${m.breakdown.city.score}%</strong> (${m.breakdown.city.status})</div>
            <div>Contact: <strong>${m.breakdown.contact.score}%</strong> (${m.breakdown.contact.status})</div>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:${m.confidence_pct}%; background:${m.badge_color}"></div>
          </div>
        </div>

        <div style="margin-top:0.75rem; text-align:right;">
          <button class="btn btn-secondary" style="font-size:0.8rem; padding:0.4rem 0.8rem;" onclick="linkCandidateToExisting('${m.master_id}')">
            🔗 Select & Link to This HCP Profile
          </button>
        </div>
      </div>
    `).join("")}
  `;

  backdrop.classList.add("active");
}

function closeModal() {
  document.getElementById("modal-backdrop").classList.remove("active");
}

async function linkCandidateToExisting(masterId) {
  const candidate = getMedRepInput();
  try {
    const res = await fetch(`${API_BASE}/link-existing`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate, master_id: masterId })
    });
    const data = await res.json();
    if (data.status === "success") {
      alert(`Success!\n\n${data.message}`);
      closeModal();
      resetFormInput();
      loadMasterlist();
    }
  } catch (e) {
    console.error("Link existing error:", e);
  }
}

async function submitMedRepEntry() {
  const candidate = getMedRepInput();
  const missing = validateMandatoryInput(candidate);

  if (missing.length > 0) {
    showWarningModal(missing);
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate })
    });
    const data = await res.json();
    if (data.status === "success") {
      alert(`Submission Processed!\n\nAction Taken: ${data.action_taken}\n${data.message}`);
      closeModal();
      resetFormInput();
      
      if (data.action_taken === "PENDING_MANAGER_REVIEW" || data.action_taken === "NEW_DOCTOR_QUEUED_FOR_VERIFICATION") {
        await loadReviews();
        switchTab("tab-reviews");
      } else {
        await loadMasterlist();
      }
    }
  } catch (e) {
    console.error("Submission error:", e);
    alert("Submission error: " + e.message);
  }
}

async function escalateReview(reviewId) {
  const actor = prompt("Enter your Name/Role for Escalation Audit:", "District Sales Manager");
  if (!actor) return;
  const reason = prompt("Enter Escalation Reason (Why pass to higher manager?):", "Uncertain match score (50-50). Passed up to Regional Director.");

  try {
    const res = await fetch(`${API_BASE}/escalate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review_id: reviewId, actor_name: actor, reason: reason })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.message);
      loadReviews();
    } else {
      alert(data.message);
    }
  } catch (e) {
    console.error("Escalation error:", e);
  }
}

async function resolveReview(reviewId, action, targetMasterId) {
  const actor = prompt("Enter your Name/Role for Audit Log:", "Regional Director / Head Steward");
  if (!actor) return;

  try {
    const res = await fetch(`${API_BASE}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        review_id: reviewId,
        action: action,
        actor_name: actor,
        target_master_id: targetMasterId
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.message);
      await loadReviews();
      await loadMasterlist();
      await loadDictionary();
    }
  } catch (e) {
    console.error("Resolution error:", e);
  }
}

function openDictionaryModal(doctorNameQuery) {
  const modal = document.getElementById("dict-modal-backdrop");
  const content = document.getElementById("dict-modal-body");

  const matches = dictionaryData.filter(d => 
    d.name.toLowerCase().includes(doctorNameQuery.toLowerCase()) || 
    d.full_canonical_name.toLowerCase().includes(doctorNameQuery.toLowerCase())
  );

  const displayList = matches.length > 0 ? matches : dictionaryData;

  content.innerHTML = `
    <p style="color:var(--text-muted); margin-bottom:1rem;">
      Viewing 100% Verified Canonical Reference Entries (Dictionary baseline data):
    </p>
    ${displayList.map(d => `
      <div style="background:rgba(15,23,42,0.8); border:1px solid var(--success); border-radius:var(--radius-md); padding:1rem; margin-bottom:1rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
          <strong style="color:var(--text-main); font-size:1.1rem;">${d.name}</strong>
          <span class="badge" style="background:rgba(16,185,129,0.2); color:#10B981;">100% ACCURATE</span>
        </div>
        <div style="font-size:0.85rem; color:var(--text-muted);">
          <div><strong>Canonical:</strong> ${d.full_canonical_name}</div>
          <div><strong>Specialty:</strong> ${d.specialty}</div>
          <div><strong>Primary Hospital:</strong> ${d.primary_hospital}</div>
          <div><strong>Secondary Clinic:</strong> ${d.secondary_hospital}</div>
          <div><strong>Official Phone:</strong> ${d.official_contact}</div>
          <div style="color:var(--primary); margin-top:0.4rem;"><em>${d.dictionary_notes}</em></div>
        </div>
      </div>
    `).join("")}
  `;

  modal.classList.add("active");
}

async function runWorkbenchTest() {
  const rec1 = {
    name: document.getElementById("wb-name1").value,
    specialty: document.getElementById("wb-spec1").value,
    hospital: document.getElementById("wb-hosp1").value,
    city: document.getElementById("wb-city1").value
  };
  const rec2 = {
    name: document.getElementById("wb-name2").value,
    specialty: document.getElementById("wb-spec2").value,
    hospital: document.getElementById("wb-hosp2").value,
    city: document.getElementById("wb-city2").value
  };

  try {
    const res = await fetch(`${API_BASE}/test-score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ record1: rec1, record2: rec2 })
    });
    const data = await res.json();
    if (data.status === "success") {
      const r = data.result;
      
      let breakdownRows = "";
      for (const [fName, fInfo] of Object.entries(r.breakdown)) {
        breakdownRows += `
          <tr>
            <td style="text-transform:capitalize"><strong>${fName}</strong></td>
            <td>${fInfo.weight_pct}</td>
            <td><strong>${fInfo.score}%</strong> (${fInfo.status})</td>
          </tr>
        `;
      }

      document.getElementById("wb-results-container").innerHTML = `
        <div style="background:rgba(15, 23, 42, 0.8); padding:1.5rem; border-radius:var(--radius-md); border:1px solid ${r.badge_color}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <h3>Calculated Confidence: <span style="color:${r.badge_color}">${r.confidence_pct}%</span></h3>
            <span class="badge" style="background:${r.badge_color}22; color:${r.badge_color}">${r.tier}</span>
          </div>
          <p style="margin-bottom:1rem; color:var(--text-muted)"><strong>Recommended Action:</strong> ${r.action}</p>

          <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.5rem;">Multi-Field Score Component Breakdown</h4>
          <table class="custom-table">
            <thead>
              <tr><th>System Field</th><th>Normalized Weight</th><th>Similarity Score & Status</th></tr>
            </thead>
            <tbody>
              ${breakdownRows}
            </tbody>
          </table>
        </div>
      `;
    }
  } catch (e) {
    console.error("Workbench error:", e);
  }
}
