const addressSelector = document.getElementById("homePageAddress");
const bloodTypeSelector = document.getElementById("bloodTypeSelector");
const form = document.getElementById("queryForm");
const submitButton = document.getElementById("submitButton");

submitButton.onclick = (e) => {
  e.preventDefault();
  let address = addressSelector.value;
  if (address) {
    address = address.trim();
  }
  let blood_type = bloodTypeSelector.value;
  form.action = `/?address=${address}&blood_type=${blood_type}`;
  form.method = "get";

  form.submit();
};
