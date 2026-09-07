$(document).ready(function () {

    // Keep the composer focused and ready to type as soon as the hood is visible.
    function focusComposer() {
        if (!$("#AuthOverlay").is(":visible")) {
            $("#Chatbox").trigger("focus");
        }
    }
    focusComposer();

    // Esc closes whichever overlay is open, without needing a mouse.
    $(document).on("keydown", function (e) {
        if (e.key !== "Escape") {
            return;
        }
        if ($("#SettingsModal").is(":visible")) {
            $("#SettingsModal").attr("hidden", true);
        } else if ($("#NotesPanel").hasClass("open")) {
            $("#NotesCloseB").trigger("click");
        }
    });
});
