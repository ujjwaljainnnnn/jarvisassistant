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

// A changing greeting for the hero heading, similar to ChatGPT/Claude's
// "Back at it, {name}" -- picked fresh each time the hood is shown, mixing
// a time-of-day-aware option in with a few fixed ones for variety.
function pickGreeting(name) {
    var hour = new Date().getHours();
    var timeGreeting =
        hour < 5 ? "Burning the midnight oil, " + name + "?" :
        hour < 12 ? "Good morning, " + name :
        hour < 17 ? "Good afternoon, " + name :
        hour < 21 ? "Good evening, " + name :
        "Working late, " + name + "?";

    var options = [
        timeGreeting,
        "Back at it, " + name,
        "Welcome back, " + name,
        "Good to see you, " + name,
        "Ready when you are, " + name,
        "What can I help with, " + name + "?",
    ];
    return options[Math.floor(Math.random() * options.length)];
}

$(document).ready(function () {

    // Esc closes whichever overlay is open, without needing a mouse.
    $(document).on("keydown", function (e) {
        if (e.key !== "Escape") {
            return;
        }
        if ($("#SettingsModal").is(":visible")) {
            $("#SettingsModal").attr("hidden", true);
        } else if ($("#ProjectMenu").is(":visible")) {
            $("#ProjectMenu").attr("hidden", true);
            $(".project-switcher").removeClass("is-open");
        } else if ($("#NotesPanel").hasClass("open")) {
            $("#NotesCloseB").trigger("click");
        }
    });
});
