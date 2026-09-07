$(document).ready(function () {

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
