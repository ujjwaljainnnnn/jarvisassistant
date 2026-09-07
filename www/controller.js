$(document).ready(function () {

    eel.expose(DisplayMessage) //displaying status/replies during voice commands and notes sessions
    function DisplayMessage(message) {
        $("#StatusText").text(message);
        $("#NotesStatus").text(message);
    }


    eel.expose(ShowHood)     //going back to hood
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#ListeningView").attr("hidden", true);
    }

    eel.expose(ShowNotesPanel)   //opening the side notes panel when a notes session starts
    function ShowNotesPanel() {
        $("#NotesRaw").empty();
        $("#NotesOrganized").text("");
        $("#NotesPanel").addClass("open");
    }

    eel.expose(AppendRawNote)   //live raw transcript as the user rambles
    function AppendRawNote(text) {
        $("#NotesRaw").append($("<p>").text(text));
        var rawEl = document.getElementById("NotesRaw");
        rawEl.scrollTop = rawEl.scrollHeight;
    }

    eel.expose(SetOrganizedNotes)   //AI-organized (or offline-cleaned) notes
    function SetOrganizedNotes(text) {
        $("#NotesOrganized").text(text);
    }

    // ----- Mic button (existing voice command flow) -----
    $("#MicB").click(function () {
        eel.playAssistantSound()
        $("#StatusText").text("Listening...");
        $("#Oval").attr("hidden", true);
        $("#ListeningView").attr("hidden", false);
        eel.allCommands()()
    });

    // ----- Typed chat (ChatB button + Enter key) -----
    function sendChatText() {
        var text = $("#Chatbox").val().trim();
        if (!text) {
            return;
        }
        $("#Chatbox").val("");
        $("#ChatResponse").text("Thinking...");
        eel.sendTextCommand(text)(function (reply) {
            $("#ChatResponse").text(reply || "");
        });
    }

    $("#ChatB").click(sendChatText);
    $("#Chatbox").on("keypress", function (e) {
        if (e.which === 13) {
            e.preventDefault();
            sendChatText();
        }
    });

    // ----- Notes panel controls -----
    $("#NotesCloseB").click(function () {
        eel.requestStopNotes()();
        $("#NotesPanel").removeClass("open");
    });
    $("#NotesStopB").click(function () {
        eel.requestStopNotes()();
    });
    $("#NotesCopyB").click(function () {
        var text = $("#NotesOrganized").text();
        if (navigator.clipboard && text) {
            navigator.clipboard.writeText(text);
        }
    });

    // ----- Settings modal -----
    function openSettings() {
        $("#SettingsModal").attr("hidden", false);
        eel.getAiStatus()(function (enabled) {
            $("#AiStatus").text(enabled ? "AI answers: enabled" : "AI answers: offline mode");
        });
    }

    function closeSettings() {
        $("#SettingsModal").attr("hidden", true);
    }

    $("#SettingsB").click(openSettings);
    $("#SettingsCloseB").click(closeSettings);
    $("#SettingsModal").on("mousedown", function (e) {
        if (e.target === this) {
            closeSettings();
        }
    });

    $("#SpeakRepliesToggle").on("change", function () {
        eel.setSpeakReplies($(this).is(":checked"))();
    });

    $("#SaveApiKeyB").click(function () {
        var key = $("#ApiKeyInput").val();
        eel.setApiKey(key)(function (enabled) {
            $("#AiStatus").text(enabled ? "AI answers: enabled" : "AI answers: offline mode");
        });
        $("#ApiKeyInput").val("");
    });

    $("#LogoutB").click(function () {
        eel.logoutUser()(function () {
            location.reload();
        });
    });

    // ----- Login / signup -----
    function setLoggedInUser(name) {
        $("#UserGreeting").text("Hi, " + name);
    }

    function showAuthOverlay(show) {
        $("#AuthOverlay").attr("hidden", !show);
    }

    function showAuthTab(tab) {
        var isLogin = tab === "login";
        $("#TabLogin").toggleClass("is-active", isLogin);
        $("#TabSignup").toggleClass("is-active", !isLogin);
        $("#LoginForm").attr("hidden", !isLogin);
        $("#SignupForm").attr("hidden", isLogin);
        $("#LoginError, #SignupError").text("");
    }

    $("#TabLogin").click(function () { showAuthTab("login"); });
    $("#TabSignup").click(function () { showAuthTab("signup"); });

    $("#LoginForm").on("submit", function (e) {
        e.preventDefault();
        var email = $("#LoginEmail").val().trim();
        var password = $("#LoginPassword").val();
        $("#LoginError").text("");
        eel.loginUser(email, password)(function (res) {
            if (res.success) {
                setLoggedInUser(res.name);
                showAuthOverlay(false);
                $("#LoginPassword").val("");
            } else {
                $("#LoginError").text(res.message);
            }
        });
    });

    $("#SignupForm").on("submit", function (e) {
        e.preventDefault();
        var name = $("#SignupName").val().trim();
        var email = $("#SignupEmail").val().trim();
        var password = $("#SignupPassword").val();
        $("#SignupError").text("");
        eel.signupUser(name, email, password)(function (res) {
            if (res.success) {
                setLoggedInUser(res.name);
                showAuthOverlay(false);
                $("#SignupPassword").val("");
            } else {
                $("#SignupError").text(res.message);
            }
        });
    });

    // On load: auto sign in if a session is remembered, otherwise show the
    // login/signup screen and block the assistant until the user is in.
    eel.getRememberedUser()(function (user) {
        if (user) {
            setLoggedInUser(user.name);
            showAuthOverlay(false);
        } else {
            showAuthOverlay(true);
            $("#Chatbox").trigger("blur");
        }
    });
});
