const { createApp } = Vue

const App = createApp({

  data() {

    return {

      username: '',
      password: '',


    }

  },

  methods: {

    login () {
      if (this.username && this.password) {
        request('/login', 'POST', {username: this.username, password: this.password})
        .then(data => {
          if (data.message === "Login successful") {
            window.location.href = 'upload.html'; 
            
            local = localStorage.setItem('token', data.token);
          } else {
            alert(data.message); // Show the error message
          }
        });
      } else {
        alert('Please enter username and password');
      }
    }

  },

})

App.mount('#vueapp')

async function request(url, method, data) {

  try {
    const headers = {}
    let body
    if (data) {
      headers['Content-Type'] = 'application/json'
      body = JSON.stringify(data)
    }

    const response = await fetch('http://localhost:8080' + url, {
      method,
      headers,
      body
    })

    return await response.json()

  }
  catch (e) {
    console.warn('Error:', e.message)
  }
}