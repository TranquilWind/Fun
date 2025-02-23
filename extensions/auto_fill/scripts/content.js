
(async function() {
  const userData = {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '1234567890',
    fullName: 'John Doe',
    address: '123 Main St, City, Country'
  };

  function matchesField(searchText, fieldType) {
    searchText = searchText.toLowerCase();
    const patterns = {
      name: /\bname\b/i,
      firstName: /\b(first|given)\s+name\b/i,
      lastName: /\b(last|family|sur)\s*name\b/i,
      phone: /\b(phone|telephone|mobile|cell|tel)\b/i,
      email: /\b(email|e-mail)\b/i,
      address: /\b(address|location|residence)\b/i
    };
    
    // Special case for name fields to avoid conflicts
    if (fieldType === 'name') {
      return patterns.name.test(searchText) && 
             !patterns.firstName.test(searchText) && 
             !patterns.lastName.test(searchText);
    }
    
    return patterns[fieldType]?.test(searchText) || false;
  }

  async function autofillForm() {
    const formInputs = document.querySelectorAll('.whsOnd.zHQkBf, input[type="text"], input[type="email"], input[type="tel"], textarea.KHxj8b');
    
    for (const input of formInputs) {
      try {
        const headingText = input.closest('.geS5n')?.querySelector('.HoXoMd .M7eMe')?.textContent || '';
        const labelText = input.closest('.Qr7Oae')?.querySelector('.M7eMe')?.textContent || '';
        const parentText = input.closest('.Xb9hP')?.textContent || '';
        const ariaLabel = input.getAttribute('aria-label') || '';
        const placeholder = input.getAttribute('placeholder') || '';
        const inputType = input.getAttribute('type') || '';
        const inputName = input.getAttribute('name') || '';
        const inputId = input.getAttribute('id') || '';
        
        const searchText = `${headingText} ${labelText} ${parentText} ${ariaLabel} ${placeholder} ${inputType} ${inputName} ${inputId}`;
        
        console.log('Searching text:', searchText); 

        
        if (matchesField(searchText, 'firstName')) {
          input.value = userData.firstName;
        } else if (matchesField(searchText, 'lastName')) {
          input.value = userData.lastName;
        } else if (matchesField(searchText, 'name')) {
          input.value = userData.fullName;
        } else if (matchesField(searchText, 'email')) {
          input.value = userData.email;
        } else if (matchesField(searchText, 'phone')) {
          input.value = userData.phone;
        } else if (matchesField(searchText, 'address')) {
          input.value = userData.address;
        }

        
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        
        
        if (input.tagName.toLowerCase() === 'textarea') {
          input.style.height = 'auto';
          input.style.height = input.scrollHeight + 'px';
        }
      } catch (error) {
        console.error('Error processing input:', error);
      }
    }
  }

  
  const existingButton = document.getElementById('autofill-form-button');
  if (!existingButton) {
    const fillButton = document.createElement('button');
    fillButton.id = 'autofill-form-button';
    fillButton.textContent = 'Autofill Form';
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
    
    fillButton.addEventListener('click', autofillForm);
    document.body.appendChild(fillButton);
  }
})();