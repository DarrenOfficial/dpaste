/*jshint strict:false */

// -----------------------------------------------------------------------------
// Add data-platform to the body tag to show platform related shortcuts
// -----------------------------------------------------------------------------
const isMac = navigator.platform.indexOf('Mac') !== -1;
document.body.dataset.platform = isMac ? 'mac' : 'win';

// -----------------------------------------------------------------------------
// Autofocus the content field on the homepage
// -----------------------------------------------------------------------------
const af = document.querySelector('.autofocus textarea');
if (af !== null) {
  af.focus();
}

// -----------------------------------------------------------------------------
// Cmd+Enter or Ctrl+Enter submits the form
// -----------------------------------------------------------------------------
document.body.onkeydown = function(e) {
  const metaKey = isMac ? e.metaKey : e.ctrlKey;
  const form = document.querySelector('.snippet-form');

  if (form && e.keyCode === 13 && metaKey) {
    form.submit();
    return false;
  }
};

// -----------------------------------------------------------------------------
// Toggle Wordwrap
// -----------------------------------------------------------------------------
const wordwrapCheckbox = document.getElementById('wordwrap');
const snippetDiv =  document.querySelectorAll('.snippet-code');

function toggleWordwrap() {
  if (wordwrapCheckbox.checked) {
    snippetDiv.forEach(i => i.classList.add('wordwrap'));
  } else {
    snippetDiv.forEach(i => i.classList.remove('wordwrap'));
  }
}

if (wordwrapCheckbox && snippetDiv) {
  toggleWordwrap();
  wordwrapCheckbox.onchange = toggleWordwrap;
}

// -----------------------------------------------------------------------------
// Right-To-Left
// -----------------------------------------------------------------------------

const rtlCheckbox = document.getElementById('id_rtl');
const snippetArea = document.getElementById('id_content');

function toggleRTL() {
  if (rtlCheckbox.checked) {
    snippetArea.dir = 'rtl';
  } else {
    snippetArea.dir = '';
  }
}

if (rtlCheckbox && snippetArea) {
  toggleRTL();
  rtlCheckbox.onchange = toggleRTL;
}

// -----------------------------------------------------------------------------
// Line Highlighting
// -----------------------------------------------------------------------------
const curLine = document.location.hash;
if (curLine.startsWith('#L')) {
  const hashlist = curLine.substring(2).split(',');
  if (hashlist.length > 0 && hashlist[0] !== '') {
    hashlist.forEach(function(el) {
      const line = document.getElementById(`l${el}`);
      if (line) {
        line.classList.add('marked');
      }
    });
  }
}

const lines = document.querySelectorAll('.snippet-code li');
lines.forEach(function(el) {
  el.onclick = function() {
    el.classList.toggle('marked');
    let hash = 'L';
    const marked = document.querySelectorAll('.snippet-code li.marked');
    marked.forEach(function(line) {
      if (hash !== 'L') {
        hash += ',';
      }
      hash += line.getAttribute('id').substring(1);
    });
    window.location.hash = hash;
  };
});

// -----------------------------------------------------------------------------
// Copy URL to Clipboard
// -----------------------------------------------------------------------------
const clipboardLink = document.getElementById('copyToClipboard');
const clipboardField = document.getElementById('copyToClipboardField');

if (clipboardLink && clipboardField) {
  clipboardLink.onclick = function(e) {
    e.preventDefault();
    clipboardField.select();
    document.execCommand('Copy');
  };
}

// -----------------------------------------------------------------------------
// Copy Snippet content to Clipboard
// -----------------------------------------------------------------------------
const snippetClipboardLink = document.getElementById('copySnippetToClipboard');
const snippetClipboardField = document.getElementById('copySnippetSource');
const snippetClipboardConfirm = document.getElementById('copy');

if (snippetClipboardLink && snippetClipboardField) {
  snippetClipboardLink.onclick = function(e) {
    e.preventDefault();
    snippetClipboardField.select();
    document.execCommand('Copy');
    snippetClipboardConfirm.style.maxHeight = '80px';
    window.scrollTo(0, 0);
  };
}

const editSnippetLink = document.getElementById('editSnippet');
const editSnippetForm = document.getElementById('edit');

if (editSnippetLink && editSnippetForm) {
  editSnippetLink.onclick = function(e) {
    e.preventDefault();
    editSnippetForm.style.display = 'block';
    window.scrollTo(
        editSnippetForm.getBoundingClientRect().x,
        editSnippetForm.getBoundingClientRect().y
    );
  };
}
