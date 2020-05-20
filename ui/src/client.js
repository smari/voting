/* eslint-disable no-undef */
const HOST = process.env.VOTESIM_HOST || 'http://localhost:5000';
const PATH_CAPABILITIES = `${HOST}${'/api/capabilities/'}`;

function getCapabilities(cb) {
  return fetch(`${PATH_CAPABILITIES}`, {
    accept: 'application/json',
  }).then(checkStatus)
    .then(parseJSON)
    .then(cb);
}

function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response;
  } else {
    const error = new Error(`HTTP Error ${response.statusText}`);
    error.status = response.statusText;
    error.response = response;
    console.log(error); // eslint-disable-line no-console
    throw error;
  }
}

function parseJSON(response) {
  return response.json();
}

const Client = { getCapabilities };
export default Client;
