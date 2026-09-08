$(document).ready(function () {

    function flashSuccess(btn, message) {
        var originalTooltip = btn.attr("data-tooltip");
        btn.addClass("is-success").attr("data-tooltip", message || "Done");
        setTimeout(function () {
            btn.removeClass("is-success").attr("data-tooltip", originalTooltip);
        }, 1400);
    }

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

    // ----- Chat transcript -----
    function scrollChatToBottom() {
        var el = document.getElementById("ChatLog");
        el.scrollTop = el.scrollHeight;
    }

    function appendBubble(role, text) {
        var bubble = $("<div>").addClass("chat-bubble chat-bubble--" + role);
        if (role === "assistant") {
            bubble.html(renderChatMarkdown(text));
        } else {
            bubble.text(text);
        }
        $("#ChatLog").append(bubble);
        scrollChatToBottom();
    }

    function showPendingBubble() {
        if ($("#PendingBubble").length) {
            return;
        }
        $("#ChatLog").append(
            '<div id="PendingBubble" class="chat-bubble chat-bubble--pending"><span></span><span></span><span></span></div>'
        );
        scrollChatToBottom();
    }

    eel.expose(AppendChatMessage)   // pushed from Python for both voice and typed turns
    function AppendChatMessage(role, text) {
        $("#PendingBubble").remove();
        appendBubble(role, text);
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
        appendBubble("user", text);
        showPendingBubble();
        eel.sendTextCommand(text)();
    }

    $("#ChatB").click(sendChatText);
    $("#Chatbox").on("keypress", function (e) {
        if (e.which === 13) {
            e.preventDefault();
            sendChatText();
        }
    });

    // ----- New chat -----
    $("#NewChatB").click(function () {
        eel.newChat()();
        $("#ChatLog").empty();
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
            navigator.clipboard.writeText(text).then(function () {
                flashSuccess($("#NotesCopyB"), "Copied!");
            });
        }
    });

    // ----- Settings modal -----
    function updateAiStatus(status) {
        status = status || {};
        $("#AiStatus").toggleClass("is-enabled", !!status.enabled);
        $("#AiStatusText").text(status.enabled ? "Connected: " + status.provider : "Offline mode");
    }

    function openSettings() {
        $("#SettingsModal").attr("hidden", false);
        eel.getAiStatus()(updateAiStatus);
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
        var provider = $("#ProviderSelect").val();
        var key = $("#ApiKeyInput").val();
        eel.setApiKey(provider, key)(function (status) {
            updateAiStatus(status);
            flashSuccess($("#SaveApiKeyB"), "Saved!");
        });
        $("#ApiKeyInput").val("");
    });

    $("#LogoutB").click(function () {
        eel.logoutUser()(function () {
            location.reload();
        });
    });

    // ----- Private mode -----
    $("#PrivateModeB").click(function () {
        var enabled = !$(this).hasClass("is-active");
        $(this).toggleClass("is-active", enabled).attr("aria-pressed", String(enabled));
        $("#PrivateModeBanner").attr("hidden", !enabled);
        eel.setPrivateMode(enabled)();
    });

    // ----- Projects -----
    function switchToProject(project) {
        $("#ProjectName").text(project.name);
        eel.switchProject(project.id || null, project.name)();
        $("#ChatLog").empty();
        closeProjectMenu();
    }

    function renderProjectList(items, currentId) {
        var list = $("#ProjectList").empty();

        function addRow(id, name) {
            var isCurrent = (id || null) === (currentId || null);
            var row = $("<button>")
                .attr("type", "button")
                .addClass("project-item")
                .toggleClass("is-current", isCurrent)
                .append(
                    $("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M20 6 9 17l-5-5'/></svg>")
                )
                .append($("<span>").text(name))
                .on("click", function () {
                    switchToProject({ id: id, name: name });
                });
            list.append(row);
        }

        addRow(null, "General");
        items.forEach(function (p) { addRow(p.id, p.name); });
    }

    function loadProjects() {
        eel.getCurrentProject()(function (current) {
            $("#ProjectName").text(current.name);
            eel.listProjects()(function (items) {
                renderProjectList(items || [], current.id);
            });
        });
    }

    function openProjectMenu() {
        $("#ProjectMenu").attr("hidden", false);
        $(".project-switcher").addClass("is-open");
        $("#ProjectButton").attr("aria-expanded", "true");
        loadProjects();
    }

    function closeProjectMenu() {
        $("#ProjectMenu").attr("hidden", true);
        $(".project-switcher").removeClass("is-open");
        $("#ProjectButton").attr("aria-expanded", "false");
        $("#ProjectError").text("");
        $("#NewProjectInput").val("");
    }

    $("#ProjectButton").click(function () {
        if ($("#ProjectMenu").is(":visible")) {
            closeProjectMenu();
        } else {
            openProjectMenu();
        }
    });

    $(document).on("mousedown", function (e) {
        if (!$(e.target).closest(".project-switcher").length) {
            closeProjectMenu();
        }
    });

    $("#NewProjectForm").on("submit", function (e) {
        e.preventDefault();
        var name = $("#NewProjectInput").val().trim();
        if (!name) {
            return;
        }
        $("#ProjectError").text("");
        eel.createProject(name)(function (res) {
            if (res.success) {
                switchToProject(res.project);
            } else {
                $("#ProjectError").text(res.message);
            }
        });
    });

    // ----- Login / signup -----
    function setLoggedInUser(user) {
        var firstName = (user.name || "").split(" ")[0] || user.name;
        $("#UserGreeting").text("Hi, " + user.name);
        $("#PromptHeading").text(pickGreeting(firstName));
        $("#AccountEmail").text(user.email || "");
        loadProjects();
    }

    function showAuthOverlay(show) {
        $("#AuthOverlay").attr("hidden", !show);
        if (!show) {
            // Only safe to focus the composer once we know it's actually
            // visible -- doing this unconditionally on page load would
            // focus it a moment before the auth overlay covers it.
            $("#Chatbox").trigger("focus");
        }
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
                setLoggedInUser(res);
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
                setLoggedInUser(res);
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
            setLoggedInUser(user);
            showAuthOverlay(false);
        } else {
            showAuthOverlay(true);
            $("#Chatbox").trigger("blur");
        }
    });
});
