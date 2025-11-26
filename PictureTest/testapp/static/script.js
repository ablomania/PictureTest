const closeIt = (objId) => {
    const obj = document.querySelector(`.${objId}`) || document.getElementById(objId);
    obj.style.display = "none";

    const form = obj.querySelector("form")
    form?.reset()
}

const openIt = (objId) => {
    (document.getElementById(objId) || document.querySelector(`.${objId}`)).style.display = "flex";
}

const openDeleteQuestionModal = ({target}) => {
    const wrapper = target.closest(".question-wrapper");
    const ref = wrapper.querySelector(".question-number");
    const questionNumber = ref.value;
    const modal = document.getElementById('delete-question-modal');
    const questionNumberInput = modal.querySelector("input[name='qnm2']");
    questionNumberInput.value = questionNumber;
    modal.querySelector(".qnm").textContent = questionNumber;
    modal.style.display = 'flex';
}

const gotoPage = (url) => {
    window.location.href = url;
}


function deleteQuestion() {
    let questionNumberInput = document.querySelector("input[name='qnm2']");
    let questionNumber = questionNumberInput ? questionNumberInput.value : null;
    if (!questionNumber) return;
    const questionNumberInputs = Array.from(document.querySelectorAll(".question-number"));
    const targetInput = questionNumberInputs.find(input => input.value === questionNumber);

    if (targetInput) {
    const wrapper = targetInput.closest('.question-wrapper');
    if (wrapper) wrapper.remove();
    }
    
    const activeQuestions = questions_count.filter(q => q.active);
    const activeCount = activeQuestions.length;

    if (activeCount > 0) {
        // Mark the last active question as inactive
        const lastActive = activeQuestions[activeCount - 1];
        lastActive.active = false;
        lastActive.sub_level = 0;
        lastActive.image_count = 0;
    }

    // Renumber and rename all visible question wrappers
    const mainNode = document.querySelector('.questions-group');
    const wrappers = Array.from(mainNode.querySelectorAll('.question-wrapper')).filter(w => w.style.display !== 'none');
    wrappers.forEach((wrapper, idx) => {
        const newNum = idx + 1;

        // Update question number input
        const qNumInput = wrapper.querySelector('.question-number');
        if (qNumInput) qNumInput.value = newNum;

        // Update label
        const label = wrapper.querySelector('.qnumber');
        if (label) label.textContent = 'Question ' + newNum;

        // Update main question textarea
        const mainQ = wrapper.querySelector('textarea[name="question"]');
        if (mainQ) {
            mainQ.name = 'question_' + newNum;
            mainQ.id = 'question-' + newNum;
        }

        // Update Quill editor ID
        const editorDiv = wrapper.querySelector('.quill-editor');
        if (editorDiv) editorDiv.id = 'editor-question-' + newNum;

        // Update sub-question inputs and editors
        const subInputs = wrapper.querySelectorAll('textarea[name^="sub_"]');
        subInputs.forEach((subInput, subIdx) => {
            subInput.name = 'sub_' + newNum;
            subInput.id = 'sub-' + newNum + '-' + (subIdx + 1);
        });

        const subEditors = wrapper.querySelectorAll('.quill-editor[id^="editor-sub-"]');
        subEditors.forEach((editor, subIdx) => {
            editor.id = 'editor-sub-' + newNum + '-' + (subIdx + 1);
        });

        // Update sub_count input
        const subCount = wrapper.querySelector('.sub_count');
        if (subCount) subCount.name = 'subcount_' + newNum;

        // Update image-button ID
        const imageBtn = wrapper.querySelector('.image-button');
        if (imageBtn) {
            imageBtn.id = 'image-button-' + newNum;
        }

        // Update image input names
        const imgInputs = wrapper.querySelectorAll('.page-image');
        imgInputs.forEach(imgInput => {
            imgInput.name = 'page_image_' + newNum;
        });
    });

    // Show "+ question" button
    const btns2 = mainNode.querySelector('.buttons2');
    if (btns2) btns2.style.display = 'flex';
}

const addImage = ({target}) => {
    let parent = target.closest(".image-wrapper");
    let wrapper = target.closest(".question-wrapper");
    let inputWrapper = parent.querySelector(".image-input-wrapper");
    let question_number = wrapper.querySelector(".question-number").value

    // Find a template input (prefer hidden template, fallback to any .page-image)
    let template = parent.querySelector(".page-image-hidden") || parent.querySelector(".page-image");
    if (!template) return;

    // Clone the input and enable it
    let clone = template.cloneNode(true);
    clone.disabled = false;
    clone.style.display = "";
    clone.name = "page_image_" + question_number
    // Remove duplicate id to avoid collisions and assign a unique id
    if (clone.id) {
        clone.removeAttribute('id');
    }
    const newId = 'page-image-' + Date.now() + '-' + Math.floor(Math.random()*1000);
    clone.id = newId;

    // Create a paired preview image and link it via a data attribute
    const previewContainer = parent.querySelector('.image-preview');
    const previewImg = document.createElement('img');
    previewImg.className = 'preview-image-dynamic';
    const previewId = 'preview-' + Date.now() + '-' + Math.floor(Math.random()*1000);
    previewImg.setAttribute('data-preview-id', previewId);
    previewImg.style.maxWidth = '100%';
    previewImg.style.maxHeight = '200px';
    previewImg.style.display = 'none';

    // Create a container for the preview image + delete button
    const previewItem = document.createElement('div');
    previewItem.className = 'preview-item';
    previewItem.style.display = 'inline-block';
    previewItem.style.margin = '6px';
    previewItem.style.textAlign = 'center';

    // Create delete button under the preview
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'image-delete-btn';
    deleteBtn.textContent = 'x';
    deleteBtn.title = 'Remove image';
    deleteBtn.style.display = 'block';
    deleteBtn.style.marginTop = '4px';
    deleteBtn.style.background = '#e57373';
    deleteBtn.style.color = '#fff';
    deleteBtn.style.border = 'none';
    deleteBtn.style.borderRadius = '4px';
    deleteBtn.style.padding = '2px 6px';
    deleteBtn.style.cursor = 'pointer';

    // Attach the linkage so previewImage can find the correct img
    clone.dataset.previewId = previewId;

    // Append preview and input
    // Append preview item (img + delete) and hidden input
    previewItem.appendChild(previewImg);
    previewItem.appendChild(deleteBtn);
    if (previewContainer) previewContainer.appendChild(previewItem);
    inputWrapper.appendChild(clone);

    // Update question metadata (image count) and button visibility
    let questionNumber = Number(wrapper.querySelector(".question-number").value);
    let question = questions_count.find(element => (
        element.number === questionNumber
    ));
    if (question) {
        question.image_count = (question.image_count || 0) + 1;
        if (question.image_count >= 2) {
            const btn = parent.querySelector(".image-button");
            if (btn) btn.style.display = "none";
        } else {
            const btn = parent.querySelector(".image-button");
            if (btn) btn.style.display = "block";
        }
    }

    // Hide the cloned file input (we use a button+preview for UX)
    clone.style.display = 'none';

    // Wire delete button to remove the preview and input
    deleteBtn.addEventListener('click', () => {
        // remove preview item
        if (previewItem && previewItem.parentNode) previewItem.parentNode.removeChild(previewItem);
        // remove the associated input(s)
        const inputs = inputWrapper.querySelectorAll(`[data-preview-id="${previewId}"]`);
        inputs.forEach(i => i.remove());

        // update question image count and toggle + button / placeholder
        if (question) {
            question.image_count = Math.max(0, (question.image_count || 1) - 1);
            const btn = parent.querySelector(".image-button");
            if (btn && question.image_count < 2) btn.style.display = 'block';
            // if no preview-item left, show the original static preview
            const wrapper = parent;
            const remaining = wrapper.querySelectorAll('.preview-item').length;
            if (remaining === 0) {
                const staticPreview = wrapper.querySelector('.image-preview > .preview-image');
                if (staticPreview) staticPreview.style.display = 'block';
            }
        }
    });

    // Trigger file selector
    clone.click();
}

// Utility: when called by previewImage, ensure linked preview-item is shown and static placeholder hidden
const showLinkedPreview = (previewId) => {
    const img = document.querySelector(`[data-preview-id="${previewId}"]`);
    if (!img) return;
    img.style.display = 'block';
    const wrapper = img.closest('.image-wrapper');
    if (wrapper) {
        // hide static placeholder (the original unwrapped preview-image if present and not this one)
        const staticPreview = Array.from(wrapper.querySelectorAll('.preview-image')).find(i => i !== img && !i.closest('.preview-item'));
        if (staticPreview) staticPreview.style.display = 'none';
    }
}


const createQuestion = () => {
  let newQuestion = questions_count.find(q => !q.active);
  if (!newQuestion) return;

  const mainNode = document.querySelector('.questions-group');
  const template = document.querySelector('.question-wrapper-hidden');
  const buttons = mainNode.querySelector('.buttons2');
  const clone = template.cloneNode(true);
  const qNum = newQuestion.number;

  clone.style.display = 'grid';
  clone.className = 'question-wrapper';

  // Update label
  const label = clone.querySelector('.qnumber');
  if (label) label.textContent = 'Question ' + qNum;

  // Update input names and IDs
  clone.querySelector('.page-image').name = 'page_image_' + qNum;
  clone.querySelector('.question-number').value = qNum;
  clone.querySelector('.question-number').disabled = false;

  const questionInput = clone.querySelector('textarea[name="question"]');
  questionInput.name = 'question';
  questionInput.id = 'question-' + qNum;
  questionInput.disabled = false;
  mainNode.insertBefore(clone, buttons);

  const questionEditorDiv = clone.querySelector('#editor-question-template');
  questionEditorDiv.id = 'editor-question-' + qNum;

  // Initialize Quill
  const quill = new Quill('#editor-question-' + qNum, quillConfigs);
  quill.on('text-change', () => {
    questionInput.value = quill.root.innerHTML;
  });
  quillInstances['question_' + qNum] = quill;

  questions_count[newQuestion.index].active = true;
};

const createSub = ({ target }) => {
  const wrapper = target.closest('.question-wrapper');
  const qNum = Number(wrapper.querySelector('.question-number').value);
  const index = questions_count.findIndex(q => q.number === qNum);
  if (index === -1 || questions_count[index].sub_level >= 6) return;

  const subQuestions = wrapper.querySelector('.sub-questions');
  const template = subQuestions.querySelector('.sub-hidden');
  const buttons = subQuestions.querySelector('.buttons');
  const clone = template.cloneNode(true);
  const subEditorDiv = clone.querySelector('.quill-editor');
  const alpha = { 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f' };

  const subLevel = questions_count[index].sub_level + 1;

  clone.style.display = 'flex';
  clone.className = 'field-wrapper';

  // Update label
  const label = clone.querySelector('.sub_label');
  if (label) label.textContent = alpha[subLevel];

  // Update input
  const subInput = clone.querySelector('textarea');
  subInput.disabled = false;
  subInput.name = 'sub_' + qNum;
  subInput.id = 'sub-' + qNum + '-' + subLevel;

  // Update subCounter
  const subCounter = wrapper.querySelector('.sub_count');
  subCounter.value = subLevel;
  subCounter.name = 'subcount_' + qNum;
  subCounter.disabled = false;

  // Update editor
  clone.querySelector('.quill-wrapper').style.display = 'block';
  subEditorDiv.id = 'editor-sub-' + qNum + '-' + subLevel;
  subEditorDiv.style.display = 'block';
  subEditorDiv.innerHTML = '';

  // Insert into DOM before initializing Quill
  subQuestions.insertBefore(clone, buttons);
  const subQuill = new Quill('#' + subEditorDiv.id, quillConfigs);
  subQuill.on('text-change', () => {
    subInput.value = subQuill.root.innerHTML;
  });
  quillInstances['sub_' + qNum + '_' + subLevel] = subQuill;

  // Add delete button
  const delBtn = document.createElement('button');
  delBtn.type = 'button';
  delBtn.className = 'delete-sub-btn';
  delBtn.textContent = '🗑';
  delBtn.title = 'Delete sub-question';
  Object.assign(delBtn.style, {
    marginLeft: '8px',
    background: '#e57373',
    color: '#fff',
    border: 'none',
    borderRadius: '50%',
    width: '28px',
    height: '28px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 2px 6px rgba(229,115,115,0.15)',
    transition: 'background 0.2s, transform 0.1s'
  });
  delBtn.onmouseover = () => { delBtn.style.background = '#c62828'; delBtn.style.transform = 'scale(1.08)'; };
  delBtn.onmouseout = () => { delBtn.style.background = '#e57373'; delBtn.style.transform = 'none'; };

  delBtn.addEventListener('click', () => {
    openDeleteSubModal(clone, wrapper, subQuestions, buttons, subCounter, qNum, index, alpha);
});

  clone.appendChild(delBtn);

  // Finalize sub-level update
  questions_count[index].sub_level += 1;
  if (questions_count[index].sub_level >= 6) buttons.style.display = 'none';

  console.log('sub-level after addition:', questions_count[index].sub_level);
};



const makeBold = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<b>" + selectedText + "</b>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

const undoAction = () => {
    if (undoList.length > 1) {
        const textBox = document.getElementById("page-question");
        redoList.push(textBox.value);
        const undoValue = undoList[undoList.length-1]
        textBox.value = undoValue;
        undoList.pop();
        // // Set the preview object
        document.getElementById("preview-question").innerHTML = undoValue;
    }
}

const redoAction = () => {
    if(redoList.length > 0) {
        const textBox = document.getElementById("page-question");
        undoList.push(textBox.value);
        const redoValue = redoList[redoList.length-1];
        textBox.value = redoValue;
        redoList.pop();
        // Set the preview object
        document.getElementById("preview-question").innerHTML = redoValue;
    }
}

const makeItalic = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<i>" + selectedText + "</i>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

// const makeNewLine = () => {

// }

const makeHeading = (headingType) => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + `<h${headingType}>` + selectedText + `</h${headingType}>` + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

const makeParagraph = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<p>" + selectedText + "</p>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

const makeSuper = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<sup>" + selectedText + "</sup>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

const makeSub = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<sub>" + selectedText + "</sub>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

const makeUnderLine = () => {
    const textBox = document.getElementById("page-question");
    const start = textBox.selectionStart;
    const end = textBox.selectionEnd;
    const selectedText = textBox.value.substring(start, end);

    // Wrap with bold markers
    const newText = textBox.value.substring(0, start) + "<u>" + selectedText + "</u>" + textBox.value.substring(end);
    // set valueslist
    undoList.push(textBox.value);
    textBox.value = newText;

    // Set the preview object
    document.getElementById("preview-question").innerHTML = newText;
}

let pendingSubDelete = null;

function openDeleteSubModal(clone, wrapper, subQuestions, buttons, subCounter, qNum, index, alpha) {
    pendingSubDelete = {clone, wrapper, subQuestions, buttons, subCounter, qNum, index, alpha};
    document.getElementById('delete-sub-modal').style.display = 'flex';
}

function deleteSubQuestion() {
    if (!pendingSubDelete) return;
    const {clone, wrapper, subQuestions, buttons, subCounter, qNum, index, alpha} = pendingSubDelete;

    // Remove the clicked sub-question
    clone.remove();

    // Update sub_level
    questions_count[index].sub_level = Math.max(0, questions_count[index].sub_level - 1);

    // Show buttons if limit not reached
    if (questions_count[index].sub_level < 6) buttons.style.display = 'block';

    // Get all remaining sub-question wrappers
    const wrappers = Array.from(subQuestions.querySelectorAll('.field-wrapper')).filter(w => w.style.display !== 'none');

    // Clear all Quill instances for this question
    Object.keys(quillInstances).forEach(key => {
      if (key.startsWith('sub_' + qNum + '_')) {
        quillInstances[key].off('text-change');
        console.log(quillInstances[key]);
        delete quillInstances[key];
      }
    });

    // Reinitialize all remaining sub-questions
    wrappers.forEach((w, idx) => {
      const level = idx + 1;
      const label = w.querySelector('.sub_label');
      const subInput = w.querySelector('textarea');
      const subEditorDiv = w.querySelector('.quill-editor');
      w.querySelectorAll('.ql-toolbar').forEach(tb => tb.remove()); // Remove existing toolbars
      let existingContent = ''; // To store existing content
      if (label) label.textContent = alpha[level];
      if (subInput) {
        subInput.name = 'sub_' + qNum;
        subInput.id = 'sub-' + qNum + '-' + level;
        existingContent = subInput.value; // Store existing content
      }
      if (subEditorDiv) {
        subEditorDiv.id = 'editor-sub-' + qNum + '-' + level;
        subEditorDiv.innerHTML = '';

        const newQuill = new Quill('#' + subEditorDiv.id, quillConfigs);
        newQuill.root.innerHTML = existingContent; // Restore content
        newQuill.on('text-change', () => {
          subInput.value = newQuill.root.innerHTML;
        });
        quillInstances['sub_' + qNum + '_' + level] = newQuill;
      }
    });

    // Update subCounter
    subCounter.value = wrappers.length;
    subCounter.name = 'subcount_' + qNum;

    console.log('sub-level after deletion:', questions_count[index].sub_level);

    pendingSubDelete = null;
  };

function confirmDeleteSubQuestion() {
    if (pendingSubDelete) {
        deleteSubQuestion(
            pendingSubDelete.clone,
            pendingSubDelete.wrapper,
            pendingSubDelete.subQuestions,
            pendingSubDelete.buttons,
            pendingSubDelete.subCounter,
            pendingSubDelete.qNum,
            pendingSubDelete.index,
            pendingSubDelete.alpha
        );
        pendingSubDelete = null;
        document.getElementById('delete-sub-modal').style.display = 'none';
    }
}

window.addEventListener('DOMContentLoaded', () => {
  // ...existing Quill initialization code...

  // After quill editors are ready, attach modal delete handlers to static sub delete buttons
  const staticDeleteBtns = document.querySelectorAll('.static-delete-sub-btn');
  staticDeleteBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const field = btn.closest('.field-wrapper');
      if (!field) return;
      const subQuestions = field.closest('.sub-questions');
      const wrapper = field.closest('.question-wrapper');
      const qNum = Number(wrapper.querySelector('.question-number').value);
      const index = questions_count.findIndex(q => q.number === qNum);
      const buttons = subQuestions.querySelector('.buttons');
      const subCounter = wrapper.querySelector('.sub_count');
      const alpha = {1: 'a',2:'b',3:'c',4:'d',5:'e',6:'f'};
      // Open confirmation modal with context
      openDeleteSubModal(field, wrapper, subQuestions, buttons, subCounter, qNum, index, alpha);
    });
  });
});