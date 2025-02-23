
function capture_response() {
  let stop = false;
  let curr_chat = " ";
  function stalk_gpt() { 
      if(stop) return; 
      const new_text = document.documentElement.innerText.toString();
      if (new_text.length > curr_chat.length) {
          curr_chat = new_text;  // Update curr_chat directly with the new content
      }
      setTimeout(stalk_gpt, 10);
  }
  console.log("Capturing response...");
  stalk_gpt();
  setTimeout(() => {
      stop = true;
      console.log("Response captured!");
      console.log(curr_chat);
  }, 10000);
}



const existingButton = document.getElementById('capture-button');
if (!existingButton) {
  const fillButton = document.createElement('button');
  fillButton.id = 'capture-button';
  fillButton.textContent = 'Capture Response';
  fillButton.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-family: 'Google Sans',Roboto,Arial,sans-serif;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  `;
  
  fillButton.addEventListener('mouseenter', () => {
    fillButton.style.backgroundColor = '#1557b0';
  });
  
  fillButton.addEventListener('mouseleave', () => {
    fillButton.style.backgroundColor = '#1a73e8';
  });
  
  fillButton.addEventListener('click', capture_response);
  document.body.appendChild(fillButton);
}

