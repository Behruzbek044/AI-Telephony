const { createApp } = Vue;

const App = createApp({
  data() {
    return {
      file: null,
      fileName: '',
      list_plans: [],
    };
  },

  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
      this.fileName = this.file ? this.file.name : '';
    },

    uploadFile() {
      if (this.file) {
        const formData = new FormData();
        formData.append('file', this.file);
        
        request('/upload', 'POST', formData)
          .then(data => {
            if (data) {
              this.list_plans = data;
            } else {
              alert('Failed to upload file.');
            }
          })
          .catch(error => {
            alert('An error occurred during file upload.');
            console.error('Error uploading file:', error);
          });
      } else {
        alert('Please select a file to upload');
      }
    },

    call(item) {
      request('/call', 'POST', JSON.stringify(item))
        .then(data => {
          console.log(data);
        })
        .catch(error => {
          alert('An error occurred during the call.');
          console.error('Error during the call:', error);
        });
    },

    getPlans() {
      request('/getplan', 'POST')
        .then(data => {
          if (data) {
            
            
            this.list_plans = data;
          } else {
            alert('Failed to fetch initial data.');
          }
        })
        .catch(error => {
          alert('An error occurred during fetching initial data.');
          console.error('Error fetching initial data:', error);
        });
    }
  },

  mounted() {
    // Fetch initial data when the component is mounted
    this.getPlans();
  }
});

App.mount('#vueapp');

async function request(url, method, data) {
  try {
    const response = await fetch('http://localhost:8080' + url, {
      method,
      body: method === 'POST' ? data : null, // Only include body if it's a POST request
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
  catch (e) {
    console.warn('Error:', e.message);
    return null; // Return null if there was an error to handle it in the calling function
  }
}
