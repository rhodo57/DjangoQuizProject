window.onload = function() {
    sumQuestions();
}

// /////////////////////////////////////////////////////////////////

  // Calculate number of questions available in selected categories
  // Warn if insufficient questions for length of quiz
  function sumQuestions() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const counterSpan = document. getElementById('counter');
    const numberField = document.getElementById('q_num');
    const divWarn = document.getElementById('q_warn');
    const btnQuiz = document.getElementById('q_but');
    let checkedValues = 0;

    for (let i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            checkedValues += Number(checkboxes[i].value);
        }
    }
    counterSpan.innerText = checkedValues.toString();

    if (numberField.valueAsNumber > checkedValues) {
        btnQuiz.disabled = true;
        divWarn.style.display = 'block';
      } else {
        btnQuiz.disabled = false;
        divWarn.style.display = 'none';
    }
  }

// /////////////////////////////////////////////////////////////////
// PASSWORD STRENGTH BAR

document.addEventListener('DOMContentLoaded', function () {
    const passwordField = document.querySelector('input[id="id_password1"]');
    const strengthBar = document.getElementById('password-strength-bar');
    const strengthText = document.getElementById('password-strength-text');

    const tips = {
        length: document.getElementById('tip-length'),
        uppercase: document.getElementById('tip-uppercase'),
        lowercase: document.getElementById('tip-lowercase'),
        number: document.getElementById('tip-number'),
        symbol: document.getElementById('tip-symbol'),
    };

    function updateTip(tipElement, passed) {
        tipElement.textContent = `${passed ? '✅' : '❌'} ${tipElement.textContent.slice(2)}`;
        tipElement.className = passed ? 'has-text-success' : 'has-text-danger';
    }

    passwordField.addEventListener('input', function () {
        const pwd = passwordField.value;
        let score = 0;

        const checks = {
            length: pwd.length >= 8,
            uppercase: /[A-Z]/.test(pwd),
            lowercase: /[a-z]/.test(pwd),
            number: /\d/.test(pwd),
            symbol: /[^A-Za-z0-9]/.test(pwd),
        };

        for (const [rule, passed] of Object.entries(checks)) {
            updateTip(tips[rule], passed);
            if (passed) score += 1;
        }

        // Update strength bar
        const percent = (score / 5) * 100;
        strengthBar.value = percent;

        if (score === 0) {
            strengthText.textContent = "Start typing to see strength.";
            strengthBar.className = "progress is-small";
        } else if (score < 3) {
            strengthText.textContent = "Weak password";
            strengthBar.className = "progress is-small is-danger";
        } else if (score < 5) {
            strengthText.textContent = "Moderate password";
            strengthBar.className = "progress is-small is-warning";
        } else {
            strengthText.textContent = "Strong password 💪";
            strengthBar.className = "progress is-small is-success";
        }
    });
});

// /////////////////////////////////////////////////////////////////
// SHOW PASSWORD TOGGLE

var x = document.getElementById("id_password1");   // Input
var s = document.getElementById("Layer_1");               // Show pass
var h = document.getElementById("Layer_2");               // Hide pass

function togglePass() {
    if (x.type === "password") {
        x.type = 'text';
        s.style.display = 'none';
        h.style.display = 'inline';
    } else {
        x.type = 'password';
        s.style.display = 'inline';
        h.style.display = 'none';
    }
}

