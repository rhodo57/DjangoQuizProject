window.onload = function() {
    sumQuestions();
}




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

