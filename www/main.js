// Small, dependency-free markdown renderer for chat bubbles. Text is
// HTML-escaped FIRST, then formatting is layered on top of the escaped
// string -- so nothing the model (or a mis-typed message) contains can
// ever inject real HTML/script into the page.
function escapeHtml(text) {
    return $("<div>").text(text == null ? "" : String(text)).html();
}

function renderChatMarkdown(text) {
    var html = escapeHtml(text);

    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>");

    var lines = html.split("\n");
    var out = [];
    var inList = false;
    lines.forEach(function (line) {
        var match = line.match(/^\s*[-*]\s+(.*)$/);
        if (match) {
            if (!inList) {
                out.push("<ul>");
                inList = true;
            }
            out.push("<li>" + match[1] + "</li>");
        } else {
            if (inList) {
                out.push("</ul>");
                inList = false;
            }
            out.push(line === "" ? "" : "<p>" + line + "</p>");
        }
    });
    if (inList) {
        out.push("</ul>");
    }

    return out.join("");
}

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
