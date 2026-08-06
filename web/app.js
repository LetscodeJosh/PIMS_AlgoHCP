/**
 * PIMS_AlgoHCP Client Application Logic
 * Supports Clean Slate Mode, Dynamic MedRep Entry Simulation, Conditional Merge Audit Visibility,
 * Auto-Dismissing Submission Toasts, and Zero-Match Fuzzy Penalty Score Calculation.
 */

const API_BASE = window.location.origin + "/api";

let currentMatches = [];
let pendingReviews = [];
let dictionaryData = [];
let masterlistData = [];
let mergeHistoryData = [];
let autoDetectDebounceTimer = null;

let sigCanvas, sigCtx;
let isDrawing = false;
let hasSignatureDrawn = false;
let deferredPrompt = null;
let fitCanvasResolutionGlobal = null;

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').then(reg => {
      console.log('[PWA] ServiceWorker registered scope:', reg.scope);
    }).catch(err => {
      console.log('[PWA] ServiceWorker registration failed:', err);
    });
  });
}

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const installBtn = document.getElementById('btn-install-pwa');
  if (installBtn) {
    installBtn.style.display = 'inline-flex';
    installBtn.addEventListener('click', () => {
      installBtn.style.display = 'none';
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('[PWA] User installed PIMS Recognizer app');
        }
        deferredPrompt = null;
      });
    });
  }
});

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupErpWizard();
  initSignaturePad();
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

  const checkBtn = document.getElementById("btn-check-recognizer");
  if (checkBtn) checkBtn.addEventListener("click", runRecognizerCheck);

  const submitBtn = document.getElementById("btn-submit-entry");
  if (submitBtn) submitBtn.addEventListener("click", submitMedRepEntry);

  const runWbBtn = document.getElementById("btn-run-workbench");
  if (runWbBtn) runWbBtn.addEventListener("click", runWorkbenchTest);

  const resetBtn = document.getElementById("btn-reset-clean-slate");
  if (resetBtn) resetBtn.addEventListener("click", resetToCleanSlate);

  const seedBtn = document.getElementById("btn-load-benchmark-preset");
  if (seedBtn) seedBtn.addEventListener("click", loadBenchmarkPresets);
  
  const warnClose = document.getElementById("warning-modal-close");
  if (warnClose) warnClose.addEventListener("click", closeWarningModal);

  const warnBtn = document.getElementById("warning-modal-btn");
  if (warnBtn) warnBtn.addEventListener("click", closeWarningModal);

  const modalClose = document.getElementById("modal-close-btn");
  if (modalClose) modalClose.addEventListener("click", closeModal);

  const modalCancel = document.getElementById("modal-cancel-btn");
  if (modalCancel) modalCancel.addEventListener("click", closeModal);
  
  const snapClose = document.getElementById("snapshot-modal-close");
  if (snapClose) snapClose.addEventListener("click", closeSnapshotModal);

  const dictClose = document.getElementById("dict-modal-close");
  if (dictClose) dictClose.addEventListener("click", () => {
    document.getElementById("dict-modal-backdrop").classList.remove("active");
  });

  triggerAutoDetect();
});

// Signature Canvas Handling
function initSignaturePad() {
  sigCanvas = document.getElementById("sig-canvas");
  if (!sigCanvas) return;
  sigCtx = sigCanvas.getContext("2d", { willReadFrequently: true });

  function setupCanvasDimensions() {
    if (!sigCanvas) return;
    const rect = sigCanvas.getBoundingClientRect();
    const w = Math.round(rect.width || 500);
    const h = Math.round(rect.height || 120);
    
    if (sigCanvas.width !== w || sigCanvas.height !== h) {
      sigCanvas.width = w;
      sigCanvas.height = h;
    }
    
    sigCtx.strokeStyle = "#38BDF8";
    sigCtx.lineWidth = 3.5;
    sigCtx.lineCap = "round";
    sigCtx.lineJoin = "round";
  }

  fitCanvasResolutionGlobal = setupCanvasDimensions;
  setupCanvasDimensions();
  window.addEventListener("resize", setupCanvasDimensions);

  function getPos(e) {
    const rect = sigCanvas.getBoundingClientRect();
    let cx = e.clientX;
    let cy = e.clientY;

    if (e.touches && e.touches.length > 0) {
      cx = e.touches[0].clientX;
      cy = e.touches[0].clientY;
    }

    const scaleX = sigCanvas.width / (rect.width || 1);
    const scaleY = sigCanvas.height / (rect.height || 1);

    return {
      x: (cx - rect.left) * scaleX,
      y: (cy - rect.top) * scaleY
    };
  }

  function handleStart(e) {
    if (e.cancelable && e.type !== "mousedown") {
      e.preventDefault();
    }

    isDrawing = true;
    hasSignatureDrawn = true;
    const pad = document.getElementById("sig-pad-wrapper");
    if (pad) pad.style.borderColor = "var(--primary)";

    const p = getPos(e);
    sigCtx.strokeStyle = "#38BDF8";
    sigCtx.fillStyle = "#38BDF8";
    sigCtx.lineWidth = 3.5;
    sigCtx.lineCap = "round";
    sigCtx.lineJoin = "round";

    sigCtx.beginPath();
    sigCtx.arc(p.x, p.y, 1.8, 0, Math.PI * 2);
    sigCtx.fill();

    sigCtx.beginPath();
    sigCtx.moveTo(p.x, p.y);
  }

  function handleMove(e) {
    if (!isDrawing || !sigCtx) return;
    if (e.cancelable && e.type !== "mousemove") {
      e.preventDefault();
    }

    const p = getPos(e);
    sigCtx.strokeStyle = "#38BDF8";
    sigCtx.lineWidth = 3.5;
    sigCtx.lineCap = "round";
    sigCtx.lineJoin = "round";

    sigCtx.lineTo(p.x, p.y);
    sigCtx.stroke();
  }

  function handleEnd() {
    if (isDrawing) {
      isDrawing = false;
      checkAndToggleErpSteps();
    }
  }

  // Bind single event model: PointerEvents if available, else Mouse+Touch
  if (window.PointerEvent) {
    sigCanvas.addEventListener("pointerdown", handleStart, { passive: false });
    sigCanvas.addEventListener("pointermove", handleMove, { passive: false });
    window.addEventListener("pointerup", handleEnd);
    window.addEventListener("pointercancel", handleEnd);
  } else {
    sigCanvas.addEventListener("mousedown", handleStart);
    sigCanvas.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleEnd);

    sigCanvas.addEventListener("touchstart", handleStart, { passive: false });
    sigCanvas.addEventListener("touchmove", handleMove, { passive: false });
    window.addEventListener("touchend", handleEnd);
  }

  const clearBtn = document.getElementById("btn-clear-sig");
  if (clearBtn) clearBtn.addEventListener("click", clearSignaturePad);
}

function clearSignaturePad() {
  if (!sigCtx || !sigCanvas) return;
  sigCtx.clearRect(0, 0, sigCanvas.width, sigCanvas.height);
  sigCtx.strokeStyle = "#38BDF8";
  sigCtx.lineWidth = 3.5;
  sigCtx.lineCap = "round";
  sigCtx.lineJoin = "round";
  hasSignatureDrawn = false;
  const pad = document.getElementById("sig-pad-wrapper");
  if (pad) pad.style.borderColor = "var(--border-color)";
  checkAndToggleErpSteps();
}

function drawSampleSignature() {
  clearSignaturePad();
  sigCtx.beginPath();
  sigCtx.moveTo(40, 45);
  sigCtx.bezierCurveTo(90, 10, 140, 70, 190, 30);
  sigCtx.bezierCurveTo(240, 60, 290, 15, 340, 40);
  sigCtx.stroke();
  hasSignatureDrawn = true;
  document.getElementById("sig-pad-wrapper").style.borderColor = "var(--primary)";
}

function getSignatureDataUrl() {
  if (!hasSignatureDrawn) return "";
  return sigCanvas ? sigCanvas.toDataURL("image/png") : "";
}

// Clean Slate & Preset Dataset Handlers
async function resetToCleanSlate() {
  if (!confirm("Are you sure you want to reset all data to a Clean Slate? Masterlist, Dictionary, and Reviews will be cleared so you can simulate real-world MedRep encoding from day 1.")) return;

  try {
    const res = await fetch(`${API_BASE}/reset-data`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      showSubmissionToast({ name: "Clean Slate Initialized", specialty: "Database Reset", hospital: "PIMS System", city: "All Data Cleared" }, "CLEAN_SLATE_RESET", data.message);
      resetFormInput();
      await loadMasterlist();
      await loadDictionary();
      await loadReviews();
    }
  } catch (e) {
    console.error("Reset error:", e);
  }
}

async function loadBenchmarkPresets() {
  try {
    const res = await fetch(`${API_BASE}/seed-data`, { method: "POST" });
    const data = await res.json();
    if (data.status === "success") {
      showSubmissionToast({ name: "Benchmark Dataset Loaded", specialty: "Demo Presets", hospital: "PIMS System", city: "Sample Data Ready" }, "BENCHMARK_DATA_LOADED", data.message);
      await loadMasterlist();
      await loadDictionary();
      await loadReviews();
    }
  } catch (e) {
    console.error("Seed error:", e);
  }
}

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

      if (targetId === "tab-medrep") {
        if (fitCanvasResolutionGlobal) fitCanvasResolutionGlobal();
      }
      if (targetId === "tab-reviews") loadReviews();
      if (targetId === "tab-masterlist") loadMasterlist();
      if (targetId === "tab-dictionary") loadDictionary();
    });
  });
}

function switchTab(tabId) {
  const tabBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  if (tabBtn) tabBtn.click();
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

  drawSampleSignature();
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

  if (!candidate.name || candidate.name.trim().length < 2) {
    bannerTitle.textContent = "Version 2.0 Name-First Intelligent Pre-Detection Engine Active";
    bannerDesc.textContent = "Start typing a Doctor Name to auto-identify doctor profile & encoding frequency...";
    bannerBadge.innerHTML = `<span class="badge" style="background:rgba(255,255,255,0.1); color:var(--text-muted)">v2.0 Active</span>`;
    return;
  }

  try {
    const nameRes = await fetch(`${API_BASE}/detect-name?name=${encodeURIComponent(candidate.name)}`);
    const nameData = await nameRes.json();
    
    const res = await fetch(`${API_BASE}/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate })
    });
    const data = await res.json();

    if (data.status === "success" && data.matches.length > 0) {
      currentMatches = data.matches;
      const top = currentMatches[0];
      const nameMatch = (nameData.matches && nameData.matches.length > 0) ? nameData.matches[0] : null;
      const encCount = top.encoded_count || (nameMatch ? nameMatch.encoded_count : 1);

      const sigBadge = top.is_sig_locked
        ? `<span class="badge" style="background:rgba(239,68,68,0.25); color:#EF4444; margin-left:0.3rem;">🔒 Signature Locked (Immutable - Level 2 Approved)</span>`
        : `<span class="badge" style="background:rgba(16,185,129,0.25); color:#10B981; margin-left:0.3rem;">✍️ Signature Vector: ${top.sig_similarity_pct || 0}%</span>`;

      bannerTitle.innerHTML = `👤 Name-First Auto-Detection: <strong>${top.confidence_pct}% Match</strong> with <u>${top.master_record.name}</u> <span class="badge" style="background:rgba(245,158,11,0.25); color:#F59E0B">🔥 Encoded ${encCount}x</span> ${sigBadge}`;
      bannerDesc.textContent = `Master ID: ${top.master_id} | ${top.master_record.hospital} | ${top.master_record.specialty} | Name Linkage: ${nameMatch ? nameMatch.name_score_pct : 0}%`;

      bannerBadge.innerHTML = `
        <span class="badge" style="background:${top.badge_color}22; color:${top.badge_color}; border:1px solid ${top.badge_color}">
          ${top.tier}
        </span>
      `;
    } else {
      bannerTitle.textContent = "Version 2.0 Name-First Pre-Detection Active";
      bannerDesc.textContent = "No master matches found yet. New doctor profile will be queued for Manager Verification.";
      bannerBadge.innerHTML = `<span class="badge" style="background:rgba(239, 68, 68, 0.2); color:#EF4444">New Doctor Candidate</span>`;
    }
  } catch (e) {
    console.error("Auto detect scan error:", e);
  }
}

function setupErpWizard() {
  document.querySelectorAll(".erp-step-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const step = btn.getAttribute("data-step");
      switchErpStep(step);
    });
  });

  const saveBtn = document.getElementById("btn-save-erp-submission");
  if (saveBtn) {
    saveBtn.addEventListener("click", submitMedRepEntry);
  }

  const photoInput = document.getElementById("input-erp-photo");
  if (photoInput) {
    photoInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        const label = document.getElementById("photo-file-label");
        if (label) label.textContent = file.name;
        const reader = new FileReader();
        reader.onload = (event) => {
          const imgPreview = document.getElementById("erp-photo-img-preview");
          if (imgPreview) {
            imgPreview.src = event.target.result;
            imgPreview.style.display = "block";
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  const consentChk = document.getElementById("chk-erp-consent");
  if (consentChk) {
    consentChk.addEventListener("change", checkAndToggleErpSteps);
  }

  // Auto-parse & Auto-fill First Name, Middle Name, Last Name from HCP Search box
  const searchInput = document.getElementById("input-doc-name");
  const fnInput = document.getElementById("input-doc-fn");
  const mnInput = document.getElementById("input-doc-mn");
  const lnInput = document.getElementById("input-doc-ln");

  if (searchInput && fnInput && lnInput) {
    const handleNameSync = () => {
      const parsed = parseInputDoctorName(searchInput.value);
      fnInput.value = parsed.firstName;
      if (mnInput) mnInput.value = parsed.middleName;
      lnInput.value = parsed.lastName;
    };

    searchInput.addEventListener("input", handleNameSync);
    searchInput.addEventListener("keyup", handleNameSync);
    searchInput.addEventListener("change", handleNameSync);
  }

  // Update date field
  const dateInput = document.getElementById("input-erp-sub-date");
  if (dateInput) {
    const now = new Date();
    dateInput.value = now.toISOString().slice(0, 10) + " " + now.toTimeString().slice(0, 8);
  }

  // Initialize at least 1 row for Specializations and Workplaces
  const specTbody = document.getElementById("specialization-rows-tbody");
  if (specTbody && specTbody.children.length === 0) {
    addSpecializationRow();
  }

  const workTbody = document.getElementById("workplace-rows-tbody");
  if (workTbody && workTbody.children.length === 0) {
    addWorkplaceRow();
  }

  checkAndToggleErpSteps();
}

function isStep1Valid() {
  const consent = document.getElementById("chk-erp-consent");
  const isConsentChecked = consent ? consent.checked : false;
  const sigUrl = getSignatureDataUrl();
  const isSigDrawn = hasSignatureDrawn || (sigUrl && sigUrl.length > 0);

  return {
    isValid: isConsentChecked && isSigDrawn,
    isConsentChecked,
    isSigDrawn
  };
}
window.isStep1Valid = isStep1Valid;

function checkAndToggleErpSteps() {
  const check = isStep1Valid();
  const gatedButtons = document.querySelectorAll(".erp-gated-step");
  const lockMsg = document.getElementById("erp-step-lock-msg");

  if (check.isValid) {
    gatedButtons.forEach(btn => {
      btn.style.display = "inline-flex";
    });
    if (lockMsg) {
      lockMsg.innerHTML = `<span style="color:#10B981; font-weight:600;">🔓 Step 1 Accomplished! Remaining Steps Unlocked</span>`;
    }
  } else {
    gatedButtons.forEach(btn => {
      btn.style.display = "none";
    });
    if (lockMsg) {
      lockMsg.innerHTML = `<span style="color:#F59E0B;">🔒 Check Consent & Sign Signature to Unlock Steps</span>`;
    }
    const activeBtn = document.querySelector(".erp-step-btn.active");
    if (activeBtn && activeBtn.getAttribute("data-step") !== "1") {
      switchErpStep("1");
    }
  }
}
window.checkAndToggleErpSteps = checkAndToggleErpSteps;

function switchErpStep(step) {
  if (step !== "1") {
    const check = isStep1Valid();
    if (!check.isValid) {
      const missing = [];
      if (!check.isConsentChecked) missing.push("Privacy Notice & Consent Checkbox");
      if (!check.isSigDrawn) missing.push("Doctor Digital Signature");

      const pad = document.getElementById("sig-pad-wrapper");
      if (pad && !check.isSigDrawn) pad.style.borderColor = "#EF4444";

      showWarningModal(missing);
      return false;
    }
  }

  document.querySelectorAll(".erp-step-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".erp-step-content").forEach(c => c.classList.remove("active"));

  const btn = document.querySelector(`.erp-step-btn[data-step="${step}"]`);
  if (btn) btn.classList.add("active");

  const content = document.getElementById(`erp-step-${step}`);
  if (content) content.classList.add("active");

  if (step === "1" && fitCanvasResolutionGlobal) {
    fitCanvasResolutionGlobal();
  }

  return true;
}
window.switchErpStep = switchErpStep;

function addSpecializationRow(spec = "", subspec = "", type = "Consultant", practice = "Prescribing") {
  const tbody = document.getElementById("specialization-rows-tbody");
  if (!tbody) return;

  const rowId = "spec-row-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
  const tr = document.createElement("tr");
  tr.id = rowId;
  tr.innerHTML = `
    <td><input type="text" class="form-control spec-name auto-detect-field" placeholder="e.g. Cardiology" value="${spec}"></td>
    <td><input type="text" class="form-control spec-subspec auto-detect-field" placeholder="e.g. Interventional Cardiology" value="${subspec}"></td>
    <td>
      <select class="form-control spec-type">
        <option value="Consultant" ${type === "Consultant" ? "selected" : ""}>Consultant</option>
        <option value="Resident" ${type === "Resident" ? "selected" : ""}>Resident</option>
        <option value="Fellow" ${type === "Fellow" ? "selected" : ""}>Fellow</option>
      </select>
    </td>
    <td>
      <select class="form-control spec-practice">
        <option value="Prescribing" ${practice === "Prescribing" ? "selected" : ""}>Prescribing</option>
        <option value="Dispensing" ${practice === "Dispensing" ? "selected" : ""}>Dispensing</option>
        <option value="Both" ${practice === "Both" ? "selected" : ""}>Both</option>
      </select>
    </td>
    <td style="text-align:center;">
      <button type="button" class="btn btn-secondary" style="font-size:0.7rem; padding:0.2rem 0.4rem; color:#EF4444;" onclick="removeRow('${rowId}', 'spec')">🗑️</button>
    </td>
  `;
  tbody.appendChild(tr);

  tr.querySelectorAll(".auto-detect-field").forEach(input => {
    input.addEventListener("keyup", triggerAutoDetect);
    input.addEventListener("change", triggerAutoDetect);
  });

  triggerAutoDetect();
}

function addWorkplaceRow(hosp = "", secHosp = "", city = "", prov = "", addr = "", contact = "", email = "") {
  const tbody = document.getElementById("workplace-rows-tbody");
  if (!tbody) return;

  const rowId = "work-row-" + Date.now() + "-" + Math.floor(Math.random() * 1000);
  const tr = document.createElement("tr");
  tr.id = rowId;
  tr.innerHTML = `
    <td><input type="text" class="form-control work-hosp auto-detect-field" placeholder="e.g. St. Lukes Hospital BGC" value="${hosp}"></td>
    <td><input type="text" class="form-control work-sec-hosp auto-detect-field" placeholder="e.g. Makati Med Annex" value="${secHosp}"></td>
    <td><input type="text" class="form-control work-city auto-detect-field" placeholder="e.g. Taguig City" value="${city}"></td>
    <td><input type="text" class="form-control work-prov auto-detect-field" placeholder="e.g. Metro Manila" value="${prov}"></td>
    <td><input type="text" class="form-control work-addr auto-detect-field" placeholder="e.g. 32nd St, BGC" value="${addr}"></td>
    <td><input type="text" class="form-control work-contact auto-detect-field" placeholder="e.g. 09171234567" value="${contact}"></td>
    <td><input type="text" class="form-control work-email auto-detect-field" placeholder="e.g. dr.cruz@stlukes.ph" value="${email}"></td>
    <td style="text-align:center;">
      <button type="button" class="btn btn-secondary" style="font-size:0.7rem; padding:0.2rem 0.4rem; color:#EF4444;" onclick="removeRow('${rowId}', 'work')">🗑️</button>
    </td>
  `;
  tbody.appendChild(tr);

  tr.querySelectorAll(".auto-detect-field").forEach(input => {
    input.addEventListener("keyup", triggerAutoDetect);
    input.addEventListener("change", triggerAutoDetect);
  });

  triggerAutoDetect();
}

function removeRow(rowId, type) {
  const row = document.getElementById(rowId);
  if (row) {
    row.remove();
  }
  if (type === "spec") {
    const tbody = document.getElementById("specialization-rows-tbody");
    if (tbody && tbody.children.length === 0) addSpecializationRow();
  } else if (type === "work") {
    const tbody = document.getElementById("workplace-rows-tbody");
    if (tbody && tbody.children.length === 0) addWorkplaceRow();
  }
  triggerAutoDetect();
}
window.addSpecializationRow = addSpecializationRow;
window.addWorkplaceRow = addWorkplaceRow;
window.removeRow = removeRow;

function getSpecializationRows() {
  const rows = [];
  document.querySelectorAll("#specialization-rows-tbody tr").forEach(tr => {
    const spec = tr.querySelector(".spec-name") ? tr.querySelector(".spec-name").value.trim() : "";
    const subspec = tr.querySelector(".spec-subspec") ? tr.querySelector(".spec-subspec").value.trim() : "";
    const type = tr.querySelector(".spec-type") ? tr.querySelector(".spec-type").value : "Consultant";
    const practice = tr.querySelector(".spec-practice") ? tr.querySelector(".spec-practice").value : "Prescribing";
    if (spec || subspec) {
      rows.push({ specialty: spec, sub_specialty: subspec, hcp_type: type, practice });
    }
  });
  return rows;
}

function getWorkplaceRows() {
  const rows = [];
  document.querySelectorAll("#workplace-rows-tbody tr").forEach(tr => {
    const hosp = tr.querySelector(".work-hosp") ? tr.querySelector(".work-hosp").value.trim() : "";
    const secHosp = tr.querySelector(".work-sec-hosp") ? tr.querySelector(".work-sec-hosp").value.trim() : "";
    const city = tr.querySelector(".work-city") ? tr.querySelector(".work-city").value.trim() : "";
    const prov = tr.querySelector(".work-prov") ? tr.querySelector(".work-prov").value.trim() : "";
    const addr = tr.querySelector(".work-addr") ? tr.querySelector(".work-addr").value.trim() : "";
    const contact = tr.querySelector(".work-contact") ? tr.querySelector(".work-contact").value.trim() : "";
    const email = tr.querySelector(".work-email") ? tr.querySelector(".work-email").value.trim() : "";
    if (hosp || city || contact) {
      rows.push({ hospital: hosp, secondary_hospital: secHosp, city, province: prov, address: addr, contact, email });
    }
  });
  return rows;
}

function getMedRepInput() {
  const fn = (document.getElementById("input-doc-fn") ? document.getElementById("input-doc-fn").value.trim() : "");
  const mn = (document.getElementById("input-doc-mn") ? document.getElementById("input-doc-mn").value.trim() : "");
  const ln = (document.getElementById("input-doc-ln") ? document.getElementById("input-doc-ln").value.trim() : "");
  const docName = (document.getElementById("input-doc-name") ? document.getElementById("input-doc-name").value.trim() : "");

  let full = docName;
  if (!full && (fn || ln)) {
    full = `Dr. ${fn} ${mn} ${ln}`.replace(/\s+/g, ' ').trim();
  }

  const specRows = getSpecializationRows();
  const workRows = getWorkplaceRows();

  const primarySpec = specRows[0] || { specialty: "", sub_specialty: "", hcp_type: "Consultant", practice: "Prescribing" };
  const primaryWork = workRows[0] || { hospital: "", secondary_hospital: "", city: "", province: "", address: "", contact: "", email: "" };

  return {
    medrep_name: "MedRep Santos",
    medrep_email: (document.getElementById("input-erp-medrep-email") ? document.getElementById("input-erp-medrep-email").value.trim() : "medrep.santos@pims.com"),
    first_name: fn,
    middle_name: mn,
    last_name: ln,
    birth_date: (document.getElementById("input-doc-dob") ? document.getElementById("input-doc-dob").value : "1980-05-15"),
    name: full,
    specializations: specRows,
    workplaces: workRows,
    specialty: primarySpec.specialty,
    sub_specialty: primarySpec.sub_specialty,
    hcp_type: primarySpec.hcp_type,
    practice: primarySpec.practice,
    hospital: primaryWork.hospital,
    secondary_hospital: primaryWork.secondary_hospital,
    address: primaryWork.address,
    city: primaryWork.city,
    province: primaryWork.province,
    contact: primaryWork.contact,
    email: primaryWork.email,
    account_program: (document.getElementById("input-erp-account-program") ? document.getElementById("input-erp-account-program").value : "Abbott Diabetes Care"),
    territory_code: (document.getElementById("input-erp-territory") ? document.getElementById("input-erp-territory").value.trim() : "TERR-NCR-SOUTH-01"),
    consent_given: (document.getElementById("chk-erp-consent") ? document.getElementById("chk-erp-consent").checked : true),
    signature_png: getSignatureDataUrl()
  };
}

function loadErpPreset(fn, mn, ln, spec, hosp, city, prov, contact, email) {
  if (document.getElementById("input-doc-fn")) document.getElementById("input-doc-fn").value = fn;
  if (document.getElementById("input-doc-mn")) document.getElementById("input-doc-mn").value = mn;
  if (document.getElementById("input-doc-ln")) document.getElementById("input-doc-ln").value = ln;
  if (document.getElementById("input-doc-name")) document.getElementById("input-doc-name").value = `Dr. ${fn} ${ln}`;

  const specTbody = document.getElementById("specialization-rows-tbody");
  if (specTbody) specTbody.innerHTML = "";
  addSpecializationRow(spec, "General Practice", "Consultant", "Prescribing");

  const workTbody = document.getElementById("workplace-rows-tbody");
  if (workTbody) workTbody.innerHTML = "";
  addWorkplaceRow(hosp, "Annex Clinic", city, prov, "Main St, Downtown", contact, email);

  switchErpStep('2');
  triggerAutoDetect();
}
window.loadErpPreset = loadErpPreset;

function validateMandatoryInput(candidate) {
  const missing = [];
  const baseFields = [
    { key: "first_name", id: "input-doc-fn", label: "First Name" },
    { key: "last_name", id: "input-doc-ln", label: "Last Name" },
    { key: "territory_code", id: "input-erp-territory", label: "Territory Code" },
    { key: "medrep_email", id: "input-erp-medrep-email", label: "Medrep Email Address" }
  ];

  baseFields.forEach(f => {
    const elem = document.getElementById(f.id);
    if (!candidate[f.key] || candidate[f.key].length === 0) {
      missing.push(f.label);
      if (elem) elem.style.borderColor = "#EF4444";
    } else {
      if (elem) elem.style.borderColor = "";
    }
  });

  if (!candidate.specialty) {
    missing.push("Specialty Name (Add at least 1 Specialization Row)");
  }

  if (!candidate.hospital) {
    missing.push("Workplace Name (Add at least 1 Workplace Row)");
  }

  if (!candidate.city) {
    missing.push("City Name");
  }

  if (!candidate.province) {
    missing.push("Province Name");
  }

  if (!candidate.contact) {
    missing.push("Mobile/Phone Number");
  }

  if (!candidate.email) {
    missing.push("Email Address");
  }

  if (!candidate.consent_given) {
    missing.push("Privacy Notice & Consent Checkbox");
  }

  if (!candidate.signature_png) {
    missing.push("Doctor Digital Signature");
    const pad = document.getElementById("sig-pad-wrapper");
    if (pad) pad.style.borderColor = "#EF4444";
  } else {
    document.getElementById("sig-pad-wrapper").style.borderColor = "var(--border-color)";
  }

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
  clearSignaturePad();
  
  document.querySelectorAll(".auto-detect-field").forEach(inp => inp.style.borderColor = "");
  triggerAutoDetect();
}

// FLOATING AUTO-DISMISSING SUBMISSION TOAST NOTIFICATION
function showSubmissionToast(submittedData, actionTaken, message) {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast-card";
  toast.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
      <strong style="color:var(--primary-light); font-size:0.85rem; text-transform:uppercase;">🚀 Submission Processed</strong>
      <span style="font-size:0.75rem; color:var(--text-muted);">${new Date().toLocaleTimeString()}</span>
    </div>
    <div style="font-weight:700; font-size:0.95rem; color:#FFFFFF;">${submittedData.name}</div>
    <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.4rem;">
      ${submittedData.specialty} | ${submittedData.hospital} | ${submittedData.city}
    </div>
    <div style="font-size:0.78rem; color:var(--success); background:rgba(16,185,129,0.15); padding:0.3rem 0.5rem; border-radius:4px;">
      <strong>Action:</strong> ${actionTaken}
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("hide");
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, 4500);
}

// CONDITIONAL READ-ONLY MERGE HISTORY SNAPSHOT MODAL
async function openMergeSnapshotModal(targetMasterId) {
  const backdrop = document.getElementById("snapshot-modal-backdrop");
  const content = document.getElementById("snapshot-modal-body");

  try {
    const res = await fetch(`${API_BASE}/merge-history`);
    const data = await res.json();
    if (data.status === "success") {
      const historyItem = data.history.find(h => h.merge_snapshot && h.merge_snapshot.master_id === targetMasterId) 
                         || data.history.find(h => h.review_id === targetMasterId) 
                         || data.history[data.history.length - 1];

      if (!historyItem || !historyItem.merge_snapshot || Object.keys(historyItem.merge_snapshot).length === 0) {
        content.innerHTML = `
          <div style="text-align:center; padding:2rem;">
            <p style="color:var(--text-muted); font-size:0.9rem;">No merge history snapshot available for this master record.</p>
            <small style="color:var(--text-dim)">Merge audit snapshots are only generated when candidate data is merged or linked into an existing Master Profile.</small>
          </div>
        `;
        backdrop.classList.add("active");
        return;
      }

      const snap = historyItem.merge_snapshot;
      const cand = snap.candidate_submitted || {};
      const before = snap.master_before || {};
      const after = snap.master_after || {};

      content.innerHTML = `
        <div style="background:rgba(239, 68, 68, 0.15); border:1px solid rgba(239, 68, 68, 0.4); padding:0.6rem 0.8rem; border-radius:var(--radius-sm); margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
          <span style="color:#EF4444; font-weight:700; font-size:0.82rem;">🔒 READ-ONLY AUDIT VIEW (CANNOT BE EDITED)</span>
          <span style="font-size:0.78rem; color:var(--text-muted)">Resolved by: ${snap.resolved_by || 'Manager'} on ${snap.resolved_at || ''}</span>
        </div>

        <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.5rem;">
          Before & After Merge Data Comparison Matrix
        </h4>

        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.75rem; margin-bottom:1rem;">
          
          <!-- Box 1: Submitted Candidate Record -->
          <div class="comp-box">
            <h4 style="color:var(--primary-light); font-size:0.82rem; margin-bottom:0.5rem;">1. Submitted Candidate (Before)</h4>
            <div class="field-pair"><div class="label">Name</div><div class="val">${cand.name || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Specialty</div><div class="val">${cand.specialty || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Hospital</div><div class="val">${cand.hospital || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Secondary</div><div class="val">${cand.secondary_hospital || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">City</div><div class="val">${cand.city || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Signature</div>
              <div class="val">
                ${cand.signature_png ? `<img src="${cand.signature_png}" style="height:30px; background:#020617; padding:2px; border-radius:4px;">` : 'N/A'}
              </div>
            </div>
          </div>

          <!-- Box 2: Master Record (Before Merge) -->
          <div class="comp-box">
            <h4 style="color:#F59E0B; font-size:0.82rem; margin-bottom:0.5rem;">2. Master Record (Before)</h4>
            <div class="field-pair"><div class="label">Master ID</div><div class="val">${before.id || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Name</div><div class="val">${before.name || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Specialty</div><div class="val">${before.specialty || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Hospital</div><div class="val">${before.hospital || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">City</div><div class="val">${before.city || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Status</div><div class="val">${before.status || 'VERIFIED'}</div></div>
          </div>

          <!-- Box 3: Final Master Record (After Merge) -->
          <div class="comp-box highlight">
            <h4 style="color:#10B981; font-size:0.82rem; margin-bottom:0.5rem;">3. Unified Master Profile (After Merge)</h4>
            <div class="field-pair"><div class="label">HCP ID</div><div class="val" style="color:#10B981">${after.id || before.id || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Canonical Name</div><div class="val" style="color:#10B981">${after.canonical_name || cand.name || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Specialty</div><div class="val">${after.specialty || cand.specialty || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Hospital</div><div class="val">${after.hospital || cand.hospital || 'N/A'}</div></div>
            <div class="field-pair"><div class="label">Status</div><div class="val" style="color:#10B981">🔒 VERIFIED_LOCKED</div></div>
            <div class="field-pair"><div class="label">True-Only-One Sig</div>
              <div class="val">
                ${(after.signature_png || cand.signature_png) ? `<img src="${after.signature_png || cand.signature_png}" style="height:30px; background:#020617; padding:2px; border-radius:4px; border:1px solid #10B981;">` : '🔒 Verified Signature Hash'}
              </div>
            </div>
          </div>

        </div>
      `;

      backdrop.classList.add("active");
    }
  } catch (e) {
    console.error("Snapshot error:", e);
  }
}

function closeSnapshotModal() {
  document.getElementById("snapshot-modal-backdrop").classList.remove("active");
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

// CONDITIONAL MERGE AUDIT BUTTON VISIBILITY IN MASTERLIST
function renderMasterlist(records) {
  const tbody = document.getElementById("masterlist-tbody");
  if (!tbody) return;

  if (records.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; padding:2.5rem; color:var(--text-muted)">
          <div style="font-size:1.5rem; margin-bottom:0.5rem;">🌱 Clean Slate Mode Active</div>
          <div>No Master Profiles in Database. Encode doctor entries under <strong>Doctor Entry</strong> tab to simulate real-world MedRep submissions!</div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = records.map(r => {
    let statusBadge = `<span class="badge" style="background:rgba(14, 165, 233, 0.15); color:var(--primary-light);">VERIFIED</span>`;
    if (r.status === "PENDING_MANAGERIAL_VERIFICATION") {
      statusBadge = `<span class="badge" style="background:rgba(245, 158, 11, 0.2); color:#F59E0B;">PENDING MANAGER VERIFICATION</span>`;
    } else if (r.status === "VERIFIED_LOCKED") {
      statusBadge = `<span class="badge" style="background:rgba(16, 185, 129, 0.2); color:#10B981;">🔒 VERIFIED & IMMUTABLE</span>`;
    }

    const encCount = r.encoded_count || 1;
    const freqBadge = `<span class="badge" style="background:rgba(245,158,11,0.25); color:#F59E0B; margin-left:0.3rem;">🔥 Encoded ${encCount}x</span>`;

    const hasMerge = r.has_merge_history === true;
    const mergeBtnHtml = hasMerge ? `
      <button class="btn btn-secondary" style="font-size:0.75rem; padding:0.3rem 0.65rem;" onclick="openMergeSnapshotModal('${r.id}')">
        👁️ View Merge Audit (Read-Only)
      </button>
    ` : `<span style="color:var(--text-dim); font-size:0.78rem;">N/A (No Merge History)</span>`;

    return `
      <tr>
        <td><strong>${r.id}</strong> ${freqBadge}<br>${statusBadge}</td>
        <td><strong>${r.name}</strong><br><small style="color:var(--text-dim)">Canonical: ${r.canonical_name}</small></td>
        <td><span class="badge" style="background:rgba(37, 99, 235, 0.2); color:var(--primary-light);">${r.specialty}</span></td>
        <td>${r.hospital}</td>
        <td>${r.city}, ${r.province || ''}</td>
        <td>${mergeBtnHtml}</td>
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

  if (records.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; padding:2.5rem; color:var(--text-muted)">
          <div style="font-size:1.5rem; margin-bottom:0.5rem;">📖 Verified Dictionary Empty</div>
          <div>When a Manager approves a New Doctor submission, canonical records and True-Only-One Signatures will auto-commit here!</div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = records.map(d => {
    const sigHtml = d.signature_png 
      ? `<img src="${d.signature_png}" style="height:30px; background:#020617; padding:2px 6px; border-radius:4px; border:1px solid #10B981;"><br><small style="color:#10B981;">🔒 Immutable Signature</small>`
      : `<span style="color:#10B981; font-size:0.78rem;">🔒 Verified Signature Hash</span>`;

    return `
      <tr>
        <td><span class="badge" style="background:rgba(16, 185, 129, 0.2); color:#10B981;">100% VERIFIED</span><br><strong>${d.id}</strong></td>
        <td><strong>${d.name}</strong><br><small style="color:var(--text-muted)">${d.full_canonical_name}</small></td>
        <td><strong>${d.specialty}</strong></td>
        <td><strong>Primary:</strong> ${d.primary_hospital}<br><small style="color:var(--text-muted)">Secondary: ${d.secondary_hospital}</small></td>
        <td>${sigHtml}</td>
        <td><small>${d.dictionary_notes}</small></td>
      </tr>
    `;
  }).join("");
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
      <div class="card" style="text-align:center; padding:2.5rem;">
        <h3 style="color:var(--text-muted); font-size:1rem;">No Pending Managerial Reviews</h3>
        <p style="color:var(--text-dim); margin-top:0.3rem; font-size:0.85rem;">All submissions and new doctor verification requests have been processed.</p>
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
      <div class="card" style="margin-bottom:1.25rem; border:1px solid ${top ? top.badge_color : 'var(--border-color)'}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;">
          <div>
            <span class="badge" style="background:rgba(245,158,11,0.2); color:#F59E0B; margin-right:0.4rem;">${rev.review_id}</span>
            <span class="badge" style="background:rgba(37, 99, 235, 0.2); color:var(--primary-light);">${rev.current_stage}</span>
            ${isNewDoctorVerification ? `<span class="badge" style="background:rgba(139,92,246,0.2); color:#8B5CF6; margin-left:0.4rem;">NEW DOCTOR VERIFICATION</span>` : ''}
          </div>
          <div style="text-align:right">
            <span style="font-size:1.25rem; font-weight:800; color:${top ? top.badge_color : '#FFF'}">${rev.confidence_pct}% Match</span>
            <div style="font-size:0.72rem; color:var(--text-dim)">Submitted: ${rev.submission_date} by ${rev.medrep_name}</div>
          </div>
        </div>

        <div style="margin-bottom:0.75rem;">
          <div class="comparison-container" style="grid-template-columns: 1fr 1fr; gap:1rem;">
            <!-- Submitted Entry (MedRep) Column -->
            <div class="comp-box" style="background:rgba(15,23,42,0.6); padding:1rem; border-radius:var(--radius-sm); border:1px solid rgba(255,255,255,0.1);">
              <h4 style="color:var(--primary-light); font-size:0.85rem; margin-bottom:0.6rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.3rem;">
                📋 Submitted Entry (MedRep Complete 4-Step Record)
              </h4>
              <div class="field-pair"><div class="label">Doctor Full Name</div><div class="val" style="color:var(--primary-light); font-weight:700;">${cand.name || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Structured Names</div><div class="val">First: ${cand.first_name || 'N/A'} | Mid: ${cand.middle_name || 'N/A'} | Last: ${cand.last_name || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Birth Date</div><div class="val">${cand.birth_date || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Specialty & Sub-Specialty</div><div class="val">${cand.specialty || 'N/A'} ${cand.sub_specialty ? '(' + cand.sub_specialty + ')' : ''}</div></div>
              <div class="field-pair"><div class="label">Type & Practice</div><div class="val">${cand.hcp_type || 'Physician'} - ${cand.practice || 'Private'}</div></div>
              <div class="field-pair"><div class="label">Primary Hospital</div><div class="val" style="font-weight:600;">${cand.hospital || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Secondary Clinic</div><div class="val">${cand.secondary_hospital || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Street Address</div><div class="val">${cand.address || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">City & Province</div><div class="val">${cand.city || 'N/A'}, ${cand.province || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Contact Number</div><div class="val">${cand.contact || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Email Address</div><div class="val">${cand.email || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Account & Territory</div><div class="val">${cand.account_program || 'N/A'} | ${cand.territory_code || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">MedRep Submitter</div><div class="val">${cand.medrep_name || 'MedRep'} (${cand.medrep_email || 'N/A'})</div></div>
              <div class="field-pair"><div class="label">Consent Checkbox</div><div class="val">${cand.consent_given ? '<span style="color:#10B981">✓ Confirmed Given</span>' : '<span style="color:#EF4444">❌ Missing</span>'}</div></div>
              <div class="field-pair" style="margin-top:0.4rem;"><div class="label">Digital Signature</div>
                <div class="val">
                  ${cand.signature_png ? `<img src="${cand.signature_png}" style="height:38px; background:#020617; padding:2px 6px; border-radius:4px; border:1px solid var(--primary);">` : '<span style="color:#EF4444">Not Signed</span>'}
                </div>
              </div>
            </div>

            <!-- Master Profile Column -->
            <div class="comp-box highlight" style="background:rgba(2,6,23,0.7); padding:1rem; border-radius:var(--radius-sm); border:1px solid rgba(16,185,129,0.3);">
              <h4 style="color:#10B981; font-size:0.85rem; margin-bottom:0.6rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.3rem;">
                ${isNewDoctorVerification ? '🛡️ Pending Master Profile (To Commit)' : '📌 Candidate Master Record (' + (mast.id || 'N/A') + ')'}
              </h4>
              <div class="field-pair"><div class="label">Master ID</div><div class="val" style="color:#10B981; font-weight:700;">${mast.id || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Doctor Full Name</div><div class="val" style="color:#10B981; font-weight:700;">${mast.name || cand.name}</div></div>
              <div class="field-pair"><div class="label">Structured Names</div><div class="val">First: ${mast.first_name || cand.first_name || 'N/A'} | Mid: ${mast.middle_name || cand.middle_name || 'N/A'} | Last: ${mast.last_name || cand.last_name || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Birth Date</div><div class="val">${mast.birth_date || cand.birth_date || '<span style="color:#F59E0B">✨ New Info to Auto-Merge</span>'}</div></div>
              <div class="field-pair"><div class="label">Specialty & Sub-Specialty</div><div class="val">${mast.specialty || cand.specialty} ${mast.sub_specialty || cand.sub_specialty ? '(' + (mast.sub_specialty || cand.sub_specialty) + ')' : ''}</div></div>
              <div class="field-pair"><div class="label">Type & Practice</div><div class="val">${mast.hcp_type || cand.hcp_type || 'Physician'} - ${mast.practice || cand.practice || 'Private'}</div></div>
              <div class="field-pair"><div class="label">Primary Hospital</div><div class="val" style="font-weight:600;">${mast.hospital || cand.hospital}</div></div>
              <div class="field-pair"><div class="label">Secondary Clinic</div><div class="val">${mast.secondary_hospital || cand.secondary_hospital || '<span style="color:#F59E0B">✨ New Info to Auto-Merge</span>'}</div></div>
              <div class="field-pair"><div class="label">Street Address</div><div class="val">${mast.address || cand.address || '<span style="color:#F59E0B">✨ New Info to Auto-Merge</span>'}</div></div>
              <div class="field-pair"><div class="label">City & Province</div><div class="val">${mast.city || cand.city}, ${mast.province || cand.province || ''}</div></div>
              <div class="field-pair"><div class="label">Contact Number</div><div class="val">${mast.contact || cand.contact || '<span style="color:#F59E0B">✨ New Info to Auto-Merge</span>'}</div></div>
              <div class="field-pair"><div class="label">Email Address</div><div class="val">${mast.email || cand.email || '<span style="color:#F59E0B">✨ New Info to Auto-Merge</span>'}</div></div>
              <div class="field-pair"><div class="label">Account & Territory</div><div class="val">${mast.account_program || cand.account_program || 'N/A'} | ${mast.territory_code || cand.territory_code || 'N/A'}</div></div>
              <div class="field-pair"><div class="label">Profile Status</div><div class="val" style="color:#F59E0B">${isNewDoctorVerification ? 'Pending Manager Lock' : (mast.status || 'Verified')}</div></div>
              <div class="field-pair" style="margin-top:0.4rem;"><div class="label">Canonical Signature Lock</div>
                <div class="val">
                  ${mast.signature_png ? `<img src="${mast.signature_png}" style="height:38px; background:#020617; padding:2px 6px; border-radius:4px; border:1px solid #10B981;"><br><small style="color:#10B981">🔒 Canonical Signature</small>` : (cand.signature_png ? `<img src="${cand.signature_png}" style="height:38px; background:#020617; padding:2px 6px; border-radius:4px; border:1px solid #F59E0B;"><br><small style="color:#F59E0B">✨ New Signature to Lock</small>` : '<span style="color:#F59E0B">Pending Lock</span>')}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div style="display:flex; gap:0.5rem">
            <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="openDictionaryModal('${cand.name}')">
              📖 Consult Dictionary
            </button>
            <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="openMergeSnapshotModal('${rev.review_id}')">
              👁️ View Merge Snapshot (Read-Only)
            </button>
          </div>

          <div style="display:flex; gap:0.4rem">
            ${rev.assigned_level < 2 ? `
              <button class="btn btn-warning" style="font-size:0.78rem;" onclick="escalateReview('${rev.review_id}')">
                ⬆️ Pass to Higher Position
              </button>
            ` : ''}
            
            ${isNewDoctorVerification ? `
              <button class="btn btn-success" style="font-size:0.78rem;" onclick="resolveReview('${rev.review_id}', 'VERIFY_AND_LOCK_CANONICAL', '${mast.id}')">
                🔒 Confirm 100% Legit Doctor Info & Commit to Masterlist
              </button>
            ` : `
              <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="resolveReview('${rev.review_id}', 'KEEP_SEPARATE', '${mast.id}')">
                ❌ Keep Separate
              </button>
              <button class="btn btn-success" style="font-size:0.78rem;" onclick="resolveReview('${rev.review_id}', 'MERGE_RECORD', '${mast.id}')">
                ✅ Higher Position Approve & Merge Master Record
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
    <div style="background:rgba(37, 99, 235, 0.15); border:1px solid var(--border-glow); padding:0.8rem; border-radius:var(--radius-sm); margin-bottom:1rem;">
      <h4 style="color:var(--primary-light); font-size:0.82rem; text-transform:uppercase; margin-bottom:0.2rem;">Submitted Candidate Input</h4>
      <div style="font-size:1rem; font-weight:700; color:#FFFFFF">${candidate.name}</div>
      <div style="font-size:0.8rem; color:var(--text-muted);">${candidate.specialty} | ${candidate.hospital} | ${candidate.city}</div>
    </div>

    <h4 style="font-size:0.85rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.6rem;">
      Algorithm Recognizer Matches (${matches.length} Master Candidates Found)
    </h4>

    ${matches.length === 0 ? `<p style="color:var(--text-muted); padding:1rem; text-align:center;">No existing master matches found. This new doctor will be queued for Manager Verification.</p>` : ''}

    ${matches.map(m => `
      <div style="background:rgba(5, 12, 30, 0.7); border:1px solid var(--border-color); border-radius:var(--radius-sm); padding:0.8rem; margin-bottom:0.75rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
          <div>
            <strong style="font-size:0.95rem; color:#FFFFFF;">${m.master_record.name}</strong>
            <small style="margin-left:0.4rem; color:var(--text-dim)">ID: ${m.master_id}</small>
          </div>
          <div>
            <span class="badge" style="background:${m.badge_color}22; color:${m.badge_color}; border:1px solid ${m.badge_color}">
              ${m.confidence_pct}% Match (${m.tier})
            </span>
          </div>
        </div>

        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">
          <strong>Hospital:</strong> ${m.master_record.hospital} | <strong>Specialty:</strong> ${m.master_record.specialty} | <strong>City:</strong> ${m.master_record.city}
        </div>

        <div style="background:rgba(0,0,0,0.3); padding:0.6rem; border-radius:4px; font-size:0.75rem;">
          <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:0.4rem; margin-bottom:0.4rem;">
            <div>Name Match: <strong>${m.breakdown.name.score}%</strong> (${m.breakdown.name.status})</div>
            <div>Specialty: <strong>${m.breakdown.specialty.score}%</strong> (${m.breakdown.specialty.status})</div>
            <div>Hospital: <strong>${m.breakdown.hospital.score}%</strong> (${m.breakdown.hospital.status})</div>
            <div>City: <strong>${m.breakdown.city.score}%</strong> (${m.breakdown.city.status})</div>
            <div>Contact: <strong>${m.breakdown.contact.score}%</strong> (${m.breakdown.contact.status})</div>
          </div>
        </div>

        <div style="margin-top:0.6rem; text-align:right;">
          <button class="btn btn-secondary" style="font-size:0.78rem; padding:0.3rem 0.7rem;" onclick="linkCandidateToExisting('${m.master_id}')">
            🔗 Select & Link to Profile
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
      showSubmissionToast(candidate, "LINKED_TO_EXISTING_RECORD", data.message);
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
      showSubmissionToast(candidate, data.action_taken, data.message);

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
  const actor = prompt("Enter Higher Position Approver Name/Role:", "Regional Director / Head Data Steward");
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
      showSubmissionToast(
        { name: `Review ${reviewId}`, specialty: "Higher Position Approval", hospital: "Verified Masterlist", city: "Metro Manila" },
        action,
        `Doctor information confirmed 100% legit by ${actor}. Profile activated in Masterlist & Dictionary to eliminate future duplicates.`
      );
      await loadReviews();
      await loadMasterlist();
      await loadDictionary();
    } else {
      alert(data.message);
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
    <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:0.75rem;">
      Viewing 100% Verified Canonical Reference Entries:
    </p>
    ${displayList.length === 0 ? `<p style="color:var(--text-muted); padding:1rem; text-align:center;">No entries in Verified Dictionary yet. Approved new doctor profiles will automatically commit here.</p>` : ''}
    ${displayList.map(d => `
      <div style="background:rgba(15,23,42,0.8); border:1px solid var(--success); border-radius:var(--radius-sm); padding:0.8rem; margin-bottom:0.75rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.3rem;">
          <strong style="color:var(--text-main); font-size:1rem;">${d.name}</strong>
          <span class="badge" style="background:rgba(16,185,129,0.2); color:#10B981;">100% ACCURATE</span>
        </div>
        <div style="font-size:0.8rem; color:var(--text-muted);">
          <div><strong>Canonical:</strong> ${d.full_canonical_name}</div>
          <div><strong>Specialty:</strong> ${d.specialty}</div>
          <div><strong>Primary Hospital:</strong> ${d.primary_hospital}</div>
          <div><strong>Secondary Clinic:</strong> ${d.secondary_hospital}</div>
          <div><strong>Official Phone:</strong> ${d.official_contact}</div>
          <div style="color:var(--primary-light); margin-top:0.3rem;"><em>${d.dictionary_notes}</em></div>
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
    secondary_hospital: document.getElementById("wb-sec-hosp1").value,
    address: document.getElementById("wb-addr1").value,
    city: document.getElementById("wb-city1").value,
    contact: document.getElementById("wb-contact1").value,
    email: document.getElementById("wb-email1").value
  };
  const rec2 = {
    name: document.getElementById("wb-name2").value,
    specialty: document.getElementById("wb-spec2").value,
    hospital: document.getElementById("wb-hosp2").value,
    secondary_hospital: document.getElementById("wb-sec-hosp2").value,
    address: document.getElementById("wb-addr2").value,
    city: document.getElementById("wb-city2").value,
    contact: document.getElementById("wb-contact2").value,
    email: document.getElementById("wb-email2").value
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
        <div style="background:rgba(15, 23, 42, 0.8); padding:1.25rem; border-radius:var(--radius-md); border:1px solid ${r.badge_color}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <h3 style="font-size:1.1rem;">Calculated Confidence: <span style="color:${r.badge_color}">${r.confidence_pct}%</span></h3>
            <span class="badge" style="background:${r.badge_color}22; color:${r.badge_color}">${r.tier}</span>
          </div>
          <p style="margin-bottom:0.75rem; font-size:0.85rem; color:var(--text-muted)"><strong>Recommended Action:</strong> ${r.action}</p>

          <h4 style="font-size:0.8rem; text-transform:uppercase; color:var(--text-muted); margin-bottom:0.4rem;">Multi-Field Score Component Breakdown</h4>
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
