window.onload = function() {
    sumQuestions();
}

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
        divWarn.textContent = 'Insufficient questions to generate quiz. Increase number of categories or decrease number of questions on quiz.'
      } else {
        btnQuiz.disabled = false;
        divWarn.textContent = ''
    }
  }

