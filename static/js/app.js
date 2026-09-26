// ==========================================================================
// Interactive UI & Experience Engine for ScholarMatch AI
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    // ----------------------------------------------------------------------
    // 1. Toast Notification Utility
    // ----------------------------------------------------------------------
    window.showToast = function(message, type = "info") {
        let container = document.getElementById("toastContainer");
        if (!container) {
            container = document.createElement("div");
            container.id = "toastContainer";
            container.className = "toast-container-custom";
            document.body.appendChild(container);
        }

        const iconMap = {
            success: "bi-check-circle-fill text-success",
            error: "bi-exclamation-triangle-fill text-danger",
            warning: "bi-exclamation-circle-fill text-warning",
            info: "bi-info-circle-fill text-primary"
        };

        const toast = document.createElement("div");
        toast.className = "custom-toast";
        toast.innerHTML = `
            <i class="bi ${iconMap[type] || iconMap.info} fs-5"></i>
            <div class="flex-grow-1 small fw-medium">${message}</div>
            <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
        `;

        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add("show"));

        const dismiss = () => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        };

        toast.querySelector(".btn-close").addEventListener("click", dismiss);
        setTimeout(dismiss, 4000);
    };

    // ----------------------------------------------------------------------
    // 2. Handle Save / Bookmark Toggling
    // ----------------------------------------------------------------------
    const saveButtons = document.querySelectorAll(".btn-toggle-save");
    saveButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const scholarshipId = btn.getAttribute("data-id");
            const isCurrentlySaved = btn.getAttribute("data-saved") === "true";

            try {
                const method = isCurrentlySaved ? "DELETE" : "POST";
                const response = await fetch(`/api/saved/${scholarshipId}`, {
                    method: method,
                    headers: { "Content-Type": "application/json" }
                });

                if (response.status === 401) {
                    showToast("Please log in to bookmark scholarships.", "warning");
                    setTimeout(() => window.location.href = "/login", 1200);
                    return;
                }

                if (response.ok) {
                    const newSavedState = !isCurrentlySaved;
                    btn.setAttribute("data-saved", newSavedState ? "true" : "false");
                    
                    if (newSavedState) {
                        btn.innerHTML = `<i class="bi bi-bookmark-check-fill text-primary"></i> <span class="d-none d-sm-inline">Saved</span>`;
                        btn.classList.add("btn-light");
                        showToast("Scholarship saved to your bookmarks!", "success");
                    } else {
                        btn.innerHTML = `<i class="bi bi-bookmark"></i> <span class="d-none d-sm-inline">Save</span>`;
                        btn.classList.remove("btn-light");
                        showToast("Scholarship removed from bookmarks.", "info");
                    }

                    // If on the /saved page, animate out the card
                    if (window.location.pathname.includes("/saved") && !newSavedState) {
                        const cardCol = btn.closest(".col-md-6, .col-lg-4");
                        if (cardCol) {
                            cardCol.style.transition = "all 0.3s ease";
                            cardCol.style.opacity = "0";
                            cardCol.style.transform = "scale(0.95)";
                            setTimeout(() => {
                                cardCol.remove();
                                const remaining = document.querySelectorAll(".col-md-6, .col-lg-4");
                                if (remaining.length === 0) {
                                    window.location.reload();
                                }
                            }, 300);
                        }
                    }
                } else {
                    const data = await response.json();
                    showToast(data.error || "Failed to update bookmark.", "error");
                }
            } catch (err) {
                console.error("Save error:", err);
                showToast("Network error updating bookmark.", "error");
            }
        });
    });

    // ----------------------------------------------------------------------
    // 3. Quick View Modal Handler
    // ----------------------------------------------------------------------
    const quickViewButtons = document.querySelectorAll(".btn-quick-view");
    const quickModalEl = document.getElementById("quickViewModal");
    
    if (quickModalEl && quickViewButtons.length > 0) {
        const bsModal = new bootstrap.Modal(quickModalEl);
        
        quickViewButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const title = btn.getAttribute("data-name") || "Scholarship Details";
                const provider = btn.getAttribute("data-provider") || "";
                const amount = btn.getAttribute("data-amount") || "Tuition Support";
                const course = btn.getAttribute("data-course") || "Any Course";
                const state = btn.getAttribute("data-state") || "All India";
                const deadline = btn.getAttribute("data-deadline") || "Ongoing";
                const desc = btn.getAttribute("data-desc") || "Visit the official portal for full eligibility criteria and submission guidelines.";
                const officialUrl = btn.getAttribute("data-url") || "#";
                const detailUrl = btn.getAttribute("data-detail-url") || "#";

                document.getElementById("qvModalTitle").textContent = title;
                document.getElementById("qvModalProvider").textContent = provider;
                document.getElementById("qvModalAmount").textContent = amount;
                document.getElementById("qvModalCourse").textContent = course;
                document.getElementById("qvModalState").textContent = state;
                document.getElementById("qvModalDeadline").textContent = deadline;
                document.getElementById("qvModalDesc").textContent = desc;
                
                const officialBtn = document.getElementById("qvModalApply");
                if (officialBtn) officialBtn.href = officialUrl;

                const detailBtn = document.getElementById("qvModalDetail");
                if (detailBtn) detailBtn.href = detailUrl;

                bsModal.show();
            });
        });
    }

    // ----------------------------------------------------------------------
    // 4. Share / Copy Link Helper
    // ----------------------------------------------------------------------
    const shareButtons = document.querySelectorAll(".btn-share-link");
    shareButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const url = btn.getAttribute("data-share-url") || window.location.href;
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(url);
                    showToast("Link copied to clipboard! 📋", "success");
                } else {
                    const tempInput = document.createElement("input");
                    tempInput.value = url;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    document.execCommand("copy");
                    document.body.removeChild(tempInput);
                    showToast("Link copied to clipboard! 📋", "success");
                }
            } catch (err) {
                showToast("Could not copy link to clipboard.", "warning");
            }
        });
    });

    // ----------------------------------------------------------------------
    // 5. Instant Client-Side Search on List / Directory
    // ----------------------------------------------------------------------
    const liveSearchInput = document.getElementById("liveSearchInput");
    const scholarshipCards = document.querySelectorAll(".scholarship-card-item");

    if (liveSearchInput && scholarshipCards.length > 0) {
        liveSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            let visibleCount = 0;

            scholarshipCards.forEach(card => {
                const title = (card.getAttribute("data-search-title") || "").toLowerCase();
                const provider = (card.getAttribute("data-search-provider") || "").toLowerCase();
                const course = (card.getAttribute("data-search-course") || "").toLowerCase();

                if (!query || title.includes(query) || provider.includes(query) || course.includes(query)) {
                    card.style.display = "";
                    visibleCount++;
                } else {
                    card.style.display = "none";
                }
            });

            const liveCountBadge = document.getElementById("liveResultCount");
            if (liveCountBadge) {
                liveCountBadge.textContent = `${visibleCount} Scholarships`;
            }
        });

        // Keyboard shortcut: pressing '/' focuses the search box
        document.addEventListener("keydown", (e) => {
            if (e.key === "/" && document.activeElement !== liveSearchInput && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
                e.preventDefault();
                liveSearchInput.focus();
                showToast("Search activated 🔍", "info");
            }
        });
    }

    // ----------------------------------------------------------------------
    // 6. Interactive Filter Chips
    // ----------------------------------------------------------------------
    const filterChips = document.querySelectorAll(".filter-chip");
    if (filterChips.length > 0 && scholarshipCards.length > 0) {
        filterChips.forEach(chip => {
            chip.addEventListener("click", () => {
                filterChips.forEach(c => c.classList.remove("active"));
                chip.classList.add("active");
                const filterVal = chip.getAttribute("data-filter") || "all";
                let count = 0;

                scholarshipCards.forEach(card => {
                    const cardCourse = card.getAttribute("data-search-course") || "";
                    const cardState = card.getAttribute("data-search-state") || "";

                    if (filterVal === "all") {
                        card.style.display = "";
                        count++;
                    } else if (filterVal === "Engineering" && (cardCourse.includes("Tech") || cardCourse.includes("Eng"))) {
                        card.style.display = "";
                        count++;
                    } else if (filterVal === "Science" && (cardCourse.includes("Sc") || cardCourse.includes("Science"))) {
                        card.style.display = "";
                        count++;
                    } else if (filterVal === "All India" && cardState === "ALL") {
                        card.style.display = "";
                        count++;
                    } else if (cardCourse.toLowerCase().includes(filterVal.toLowerCase()) || cardState.toLowerCase().includes(filterVal.toLowerCase())) {
                        card.style.display = "";
                        count++;
                    } else {
                        card.style.display = "none";
                    }
                });

                const liveCountBadge = document.getElementById("liveResultCount");
                if (liveCountBadge) {
                    liveCountBadge.textContent = `${count} Scholarships`;
                }
            });
        });
    }

    // ----------------------------------------------------------------------
    // 7. Auto-dismiss Bootstrap alerts after 4 seconds
    // ----------------------------------------------------------------------
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});
