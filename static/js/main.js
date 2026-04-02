function previewFoto(input) {
  const preview = document.getElementById('foto-preview');
  const placeholder = document.getElementById('foto-placeholder');
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.style.display = 'block';
      if (placeholder) placeholder.style.display = 'none';
    };
    reader.readAsDataURL(input.files[0]);
  }
}

function hitungNA(row) {
  const inputs = row.querySelectorAll('input[type="number"]');
  if (inputs.length < 3) return;
  const nh = parseFloat(inputs[0].value) || 0;
  const uts = parseFloat(inputs[1].value) || 0;
  const uas = parseFloat(inputs[2].value) || 0;
  const na = (nh * 0.4 + uts * 0.3 + uas * 0.3).toFixed(1);
  const display = row.querySelector('.na-display');
  if (display) {
    display.textContent = na;
    display.className = 'na-display ' + (na >= 80 ? 'green' : na >= 70 ? 'yellow' : 'red');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'all 0.3s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
    }, 4000);
    setTimeout(() => el.remove(), 4300);
  });
});
