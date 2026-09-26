// Interactive UI scripts for Scholarship Recommendation System

document.addEventListener("DOMContentLoaded", () => {
    // Handle Save / Bookmark toggling
    const saveButtons = document.querySelectorAll(".btn-toggle-save");
    saveButtons.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const scholarshipId = btn.getAttribute("data-id");
            const isCurrentlySaved = btn.getAttribute("data-saved") === "true";

            try {
                const method = isCurrentlySaved ? "DELETE" : "POST";
                const response = await fetch(`/api/saved/${scholarshipId}`, {
                    method: method,
                    headers: { "Content-Type": "application/json" }
                });

                if (response.status === 401) {
                    alert("Please log in to bookmark scholarships.");
                    window.location.href = "/login";
                    return;
                }

                if (response.ok) {
                    const newSavedState = !isCurrentlySaved;
                    btn.setAttribute("data-saved", newSavedState ? "true" : "false");
                    if (newSavedState) {
                        btn.innerHTML = `<i class="bi bi-bookmark-check-fill text-primary"></i> Saved`;
                        btn.classList.add("btn-light");
                    } else {
                        btn.innerHTML = `<i class="bi bi-bookmark"></i> Save`;
                        btn.classList.remove("btn-light");
                    }

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
                    alert(data.error || "Failed to update bookmark.");
                }
            } catch (err) {
                console.error("Save error:", err);
                alert("Network error updating bookmark.");
            }
        });
    });

    // Auto-dismiss alerts after 4 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });
});
