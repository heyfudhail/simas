/* ─── Photo Preview ─── */
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

/* ─── Hitung Nilai Akhir ─── */
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

/* ─── Sidebar Toggle (Mobile) ─── */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const icon = document.getElementById('menuIcon');
  sidebar.classList.toggle('open');
  overlay.classList.toggle('show');
  if (sidebar.classList.contains('open')) {
    icon.className = 'fas fa-times';
  } else {
    icon.className = 'fas fa-bars';
  }
}

/* ─── Modal Utilities ─── */
function openModal(id) {
  document.getElementById(id).classList.add('show');
  document.body.style.overflow = 'hidden';
}

function closeModal(id) {
  document.getElementById(id).classList.remove('show');
  document.body.style.overflow = '';
}

function closeModalOutside(event, id) {
  if (event.target === document.getElementById(id)) {
    closeModal(id);
  }
}

/* ─── Confirm Delete ─── */
function confirmDelete(name, url) {
  if (confirm('Hapus user "' + name + '"?\nTindakan ini tidak dapat dibatalkan.')) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    document.body.appendChild(form);
    form.submit();
  }
}

/* ─── Confirm Delete with custom message ─── */
function confirmAction(message, url) {
  if (confirm(message)) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    document.body.appendChild(form);
    form.submit();
  }
}

/* ─── Close modal with Escape key ─── */
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.show').forEach(m => {
      m.classList.remove('show');
      document.body.style.overflow = '';
    });
  }
});

/* ─── Auto-dismiss alerts ─── */
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
