

const closeIt = (objId) => {
    const obj = document.querySelector(`.${objId}`) || document.getElementById(objId);
    obj.style.display = "none";

    const form = obj.querySelector("form")
    form?.reset()
}

const openIt = (objId) => {
    (document.getElementById(objId) || document.querySelector(`.${objId}`)).style.display = "flex";
}

const gotoPage = (url) => {
    window.location.href = url;
}


function deleteQuestion(event) {
    const btn = event.target.closest('.delete-question-btn');
    const questionWrapper = btn.closest('.question-wrapper');
    if (!questionWrapper) return;

    // Remove the question DOM node
    questionWrapper.remove();

    // Count active questions
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
  const question = questions_count.find(q => q.number === qNum);
  if (!question || question.sub_level >= 6) return;

  const subQuestions = wrapper.querySelector('.sub-questions');
  const template = subQuestions.querySelector('.sub-hidden');
  const buttons = subQuestions.querySelector('.buttons');
  const clone = template.cloneNode(true);
  const subEditorDiv = clone.querySelector('.quill-editor');
  subEditorDiv.innerHTML = ''; // Clear any existing Quill markup
  const subLevel = question.sub_level + 1;
  subEditorDiv.id = 'editor-sub-' + qNum + '-' + subLevel;
  subEditorDiv.style.display = 'block';

  const alpha = { 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f' };

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
  const subCounter = wrapper.querySelector('.sub_count');
  subCounter.value = subLevel;
  subCounter.name = "subcount_" + qNum;
  subCounter.disabled = false;

  // Update editor
//   const subEditorDiv = clone.querySelector('.quill-editor');
  clone.querySelector(".quill-wrapper").style.display = "block";
  subEditorDiv.id = 'editor-sub-' + qNum + '-' + subLevel;
  subEditorDiv.style.display = 'block';

  // Insert into DOM before initializing Quill
  subQuestions.insertBefore(clone, buttons);
  const subQuill = new Quill('#editor-sub-' + qNum + '-' + subLevel, quillConfigs);
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
    clone.remove();
    question.sub_level = Math.max(0, question.sub_level - 1);
    if (question.sub_level < 6) buttons.style.display = 'block';

    const wrappers = Array.from(subQuestions.querySelectorAll('.field-wrapper')).filter(w => w.style.display !== 'none');
    wrappers.forEach((w, idx) => {
      const label = w.querySelector('.sub_label');
      if (label) label.textContent = alpha[idx + 1];
    });
  });

  clone.appendChild(delBtn);

  if (subLevel >= 6) buttons.style.display = 'none';
  questions_count[question.index].sub_level += 1;
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