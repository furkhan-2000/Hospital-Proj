const API_BASE = '/api';

document.getElementById('patientForm').addEventListener('submit', async e => {
  e.preventDefault();

  const payload = {
    first_name:    document.getElementById('firstName').value,
    last_name:     document.getElementById('lastName').value,
    date_of_birth: document.getElementById('dob').value,
    age:           document.getElementById('age').value,
    sex:           document.getElementById('sex').value,
    email:         document.getElementById('email').value,
    phone:         document.getElementById('phone').value,
    description:   document.getElementById('description').value
  };

  try {
    const res = await fetch(`${API_BASE}/patients`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.error || JSON.stringify(body));

    document.getElementById('patientForm').reset();
    showToast('Patient registered successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
});

function showToast(msg, type) {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.getElementById('toastContainer').appendChild(t);
  setTimeout(() => t.remove(), 5000);
}
