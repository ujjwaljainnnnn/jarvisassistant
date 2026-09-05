(function () {
    "use strict";

    var stage = document.getElementById("avatarStage");
    var blob = document.getElementById("avatarBlob");
    var blobInner = document.getElementById("blobInner");
    var caption = document.getElementById("avatarCaption");

    var eyeLeft = document.getElementById("eyeLeft");
    var eyeRight = document.getElementById("eyeRight");
    var pupilLeft = document.getElementById("pupilLeft");
    var pupilRight = document.getElementById("pupilRight");
    var browLeft = document.getElementById("browLeft");
    var browRight = document.getElementById("browRight");
    var mouth = document.getElementById("mouth");

    var form = document.getElementById("signupForm");
    var nameInput = document.getElementById("nameInput");
    var emailInput = document.getElementById("emailInput");
    var passwordInput = document.getElementById("passwordInput");
    var confirmInput = document.getElementById("confirmInput");
    var emailHint = document.getElementById("emailHint");
    var confirmHint = document.getElementById("confirmHint");
    var strengthFill = document.getElementById("strengthFill");
    var formStatus = document.getElementById("formStatus");

    var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // ---------- Mouse follow (blob tilt + eye tracking) ----------

    var mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    var tilt = { x: 0, y: 0, r: 0 };

    document.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    function clamp(v, min, max) {
        return Math.max(min, Math.min(max, v));
    }

    function pointPupil(eyeEl, pupilEl) {
        var rect = eyeEl.getBoundingClientRect();
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;
        var angle = Math.atan2(mouse.y - cy, mouse.x - cx);
        var maxRadius = 7;
        var dist = Math.min(maxRadius, Math.hypot(mouse.x - cx, mouse.y - cy) / 10);
        var px = Math.cos(angle) * dist;
        var py = Math.sin(angle) * dist;
        pupilEl.style.transform = "translate(" + px.toFixed(1) + "px, " + py.toFixed(1) + "px)";
    }

    function animate() {
        var rect = blob.getBoundingClientRect();
        var cx = rect.left + rect.width / 2;
        var cy = rect.top + rect.height / 2;

        var targetX = clamp((mouse.x - cx) / 18, -12, 12);
        var targetY = clamp((mouse.y - cy) / 22, -10, 10);
        var targetR = clamp((mouse.x - cx) / 40, -8, 8);

        tilt.x += (targetX - tilt.x) * 0.08;
        tilt.y += (targetY - tilt.y) * 0.08;
        tilt.r += (targetR - tilt.r) * 0.08;

        blob.style.transform =
            "translate(" + tilt.x.toFixed(2) + "px, " + tilt.y.toFixed(2) + "px) rotate(" + tilt.r.toFixed(2) + "deg)";

        pointPupil(eyeLeft, pupilLeft);
        pointPupil(eyeRight, pupilRight);

        requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);

    // ---------- Expression state machine ----------

    var CAPTIONS = {
        idle: "Hi! I'm Jarvis. Let's get you set up.",
        typingName: "Nice to meet you!",
        typingEmail: "Go on, I'm listening...",
        happy: "Looking good!",
        password: "I won't peek, promise 🙈",
        mismatch: "Hmm, those don't match.",
        error: "Please check the highlighted fields.",
        success: "Welcome aboard! 🎉"
    };

    var currentState = "idle";
    var talkTimer = null;

    function setEyes(mode) {
        [eyeLeft, eyeRight].forEach(function (eye) {
            eye.classList.remove("closed", "happy");
            if (mode) eye.classList.add(mode);
        });
    }

    function setBrows(mode) {
        [browLeft, browRight].forEach(function (b) {
            b.classList.remove("raised", "worried");
            if (mode) b.classList.add(mode);
        });
    }

    function setMouth(shape) {
        mouth.className = "mouth" + (shape ? " " + shape : "");
    }

    function setCaption(text) {
        caption.textContent = text;
    }

    function applyState(state, captionKey) {
        currentState = state;
        stage.className = "avatar-stage state-" + state;
        setCaption(CAPTIONS[captionKey || state] || "");

        switch (state) {
            case "happy":
                setEyes("happy");
                setBrows("raised");
                setMouth("smile");
                break;
            case "password":
                setEyes("closed");
                setBrows(null);
                setMouth("shy");
                break;
            case "mismatch":
                setEyes(null);
                setBrows("worried");
                setMouth("frown");
                break;
            case "error":
                setEyes(null);
                setBrows("worried");
                setMouth("frown");
                triggerShake();
                break;
            case "success":
                setEyes("happy");
                setBrows("raised");
                setMouth("smile");
                triggerCelebrate();
                break;
            case "typing":
                setEyes(null);
                setBrows(null);
                setMouth("flat");
                break;
            default:
                setEyes(null);
                setBrows(null);
                setMouth(null);
        }
    }

    function triggerTalk() {
        if (currentState !== "typing") return;
        mouth.classList.add("talk");
        clearTimeout(talkTimer);
        talkTimer = setTimeout(function () {
            if (currentState === "typing") mouth.classList.remove("talk");
        }, 140);
    }

    function triggerShake() {
        blobInner.classList.remove("shake");
        void blobInner.offsetWidth; // restart animation
        blobInner.classList.add("shake");
        setTimeout(function () { blobInner.classList.remove("shake"); }, 500);
    }

    function triggerCelebrate() {
        blobInner.classList.remove("celebrate");
        void blobInner.offsetWidth;
        blobInner.classList.add("celebrate");
        setTimeout(function () { blobInner.classList.remove("celebrate"); }, 1300);
    }

    function passwordsMatch() {
        return confirmInput.value.length > 0 && confirmInput.value === passwordInput.value;
    }

    function updateAvatarState(activeCaptionHint) {
        var focused = document.activeElement;

        if (focused === passwordInput) {
            applyState("password");
            return;
        }

        if (confirmInput.value.length > 0) {
            if (passwordsMatch()) {
                applyState("happy");
            } else {
                applyState("mismatch");
            }
            return;
        }

        if (focused === emailInput || activeCaptionHint === "typingEmail") {
            if (emailInput.value.length > 0 && EMAIL_RE.test(emailInput.value)) {
                applyState("happy");
            } else {
                applyState("typing", "typingEmail");
            }
            return;
        }

        if (focused === nameInput && nameInput.value.length > 0) {
            applyState("typing", "typingName");
            return;
        }

        applyState("idle");
    }

    // ---------- Field wiring ----------

    nameInput.addEventListener("focus", function () { updateAvatarState(); });
    nameInput.addEventListener("input", function () { updateAvatarState(); triggerTalk(); });
    nameInput.addEventListener("blur", function () { updateAvatarState(); });

    emailInput.addEventListener("focus", function () { updateAvatarState("typingEmail"); });
    emailInput.addEventListener("input", function () {
        updateAvatarState("typingEmail");
        triggerTalk();
        var hasValue = emailInput.value.length > 0;
        var valid = EMAIL_RE.test(emailInput.value);
        emailInput.classList.toggle("invalid", hasValue && !valid);
        emailInput.classList.toggle("valid", hasValue && valid);
        emailHint.textContent = hasValue && !valid ? "That doesn't look like a valid email." : "";
        emailHint.classList.toggle("ok", false);
    });
    emailInput.addEventListener("blur", function () { updateAvatarState(); });

    passwordInput.addEventListener("focus", function () { updateAvatarState(); });
    passwordInput.addEventListener("input", function () {
        var value = passwordInput.value;
        var score = 0;
        if (value.length >= 8) score += 35;
        if (value.length >= 12) score += 15;
        if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 20;
        if (/\d/.test(value)) score += 15;
        if (/[^A-Za-z0-9]/.test(value)) score += 15;
        strengthFill.style.width = Math.min(100, score) + "%";

        if (confirmInput.value.length > 0) {
            confirmInput.classList.toggle("valid", passwordsMatch());
            confirmInput.classList.toggle("invalid", !passwordsMatch());
            confirmHint.textContent = passwordsMatch() ? "Passwords match." : "Passwords don't match yet.";
            confirmHint.classList.toggle("ok", passwordsMatch());
        }
        updateAvatarState();
    });
    passwordInput.addEventListener("blur", function () { updateAvatarState(); });

    confirmInput.addEventListener("focus", function () { updateAvatarState(); });
    confirmInput.addEventListener("input", function () {
        var match = passwordsMatch();
        var hasValue = confirmInput.value.length > 0;
        confirmInput.classList.toggle("valid", hasValue && match);
        confirmInput.classList.toggle("invalid", hasValue && !match);
        confirmHint.textContent = hasValue ? (match ? "Passwords match." : "Passwords don't match yet.") : "";
        confirmHint.classList.toggle("ok", hasValue && match);
        updateAvatarState();
    });
    confirmInput.addEventListener("blur", function () { updateAvatarState(); });

    // ---------- Submit ----------

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        var nameOk = nameInput.value.trim().length > 0;
        var emailOk = EMAIL_RE.test(emailInput.value);
        var passwordOk = passwordInput.value.length >= 8;
        var confirmOk = passwordsMatch();

        nameInput.classList.toggle("invalid", !nameOk);
        emailInput.classList.toggle("invalid", !emailOk);
        emailInput.classList.toggle("valid", emailOk);
        passwordInput.classList.toggle("invalid", !passwordOk);
        confirmInput.classList.toggle("invalid", !confirmOk);
        confirmInput.classList.toggle("valid", confirmOk);

        if (nameOk && emailOk && passwordOk && confirmOk) {
            applyState("success");
            formStatus.textContent = "Account created — welcome, " + nameInput.value.trim() + "!";
            formStatus.className = "form-status";
        } else {
            applyState("error");
            var issues = [];
            if (!nameOk) issues.push("your name");
            if (!emailOk) issues.push("a valid email");
            if (!passwordOk) issues.push("a password of at least 8 characters");
            if (!confirmOk) issues.push("matching passwords");
            formStatus.textContent = "Please provide " + issues.join(", ") + ".";
            formStatus.className = "form-status error";
        }
    });

    applyState("idle");
})();
