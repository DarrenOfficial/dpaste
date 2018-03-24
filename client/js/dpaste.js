/*jshint strict:false */

if (typeof console === "undefined" || typeof console.log === "undefined") {
    console = {};
    console.log = function () { };
}

// -----------------------------------------------------------------------------
// Add data-platform to the body tag to show platform related shortcuts
// -----------------------------------------------------------------------------
const isWindows = navigator.appVersion.indexOf("Win") !== -1;
document.body.dataset.platform = isWindows ? 'win' : 'mac';

// -----------------------------------------------------------------------------
// Autofocus the content field on the homepage
// -----------------------------------------------------------------------------
const af = document.querySelector(".autofocus textarea");
if (af !== null) {
  af.focus();
}

// -----------------------------------------------------------------------------
// Cmd+Enter or Ctrl+Enter submits the form
// -----------------------------------------------------------------------------
document.body.onkeydown = function(e) {
  const metaKey = isWindows ? e.ctrlKey : e.metaKey;
  const form = document.querySelector(".snippet-form");

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

let lines = document.querySelectorAll('.snippet-code li');
lines.forEach(function(el) {
  el.onclick = function() {
    el.classList.toggle('marked');
    let hash = 'L';
    let marked = document.querySelectorAll('.snippet-code li.marked');
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
const copyToClipboardField = document.getElementById('copyToClipboardField');

if (clipboardLink && copyToClipboardField) {
  clipboardLink.onclick = function(e) {
    e.preventDefault();
    copyToClipboardField.select();
    document.execCommand("Copy");
    console.log('Copied URL to clipboard:', copyToClipboardField.value);
  };
}
