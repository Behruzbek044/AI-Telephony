const { createApp } = Vue;

const App = createApp({
  data() {
    return {
      call_info_list: [],  // Data for call information
    };
  },

  methods: {
    getCallInfo() {
      request('/getcallinfo', 'GET')
        .then(data => {
          if (data) {
            this.call_info_list = data;
          } else {
            alert('Failed to fetch call information.');
          }
        })
        .catch(error => {
          alert('An error occurred during fetching call information.');
          console.error('Error fetching call information:', error);
        });
    }
  },

  mounted() {
    this.getCallInfo();  // Fetch the call info when the component is mounted
  }
});

App.mount('#vueapp');

async function request(url, method, data) {
  try {
    const response = await fetch('http://localhost:8080' + url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: method === 'POST' ? JSON.stringify(data) : null,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (e) {
    console.warn('Error:', e.message);
    return null;
  }
}
