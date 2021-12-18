/**
 *  Sends a request to the rest-api, which handles database querying
 *  returns promise decodes json response and
 *  rejects on successful connection but unsuccessful query
 *  @property data.payload
 */
function databaseQuery(action, requestBody = null) {
    if (!action) return null;
    let requestInit = {};
    if (requestBody) {
        let fd = new FormData();
        for (let key in requestBody) {
            fd.append(key, requestBody[key]);
        }
        requestInit = {
            method: 'POST',
            body: fd
        };
    }
    return new Promise((resolve, reject) => {
        fetch('./rest_api?action=' + action, requestInit)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.ok) resolve(data.payload);
                else reject(data.error);
            })
            .catch(error => {
                reject(error)
            });
    });
}


/**
 * Creates on-click function for list item delete buttons
 */
function deleteButtonCallback(row) {
    let idToDelete = row.getAttribute('id');
    return () => {
        let deletePromise = databaseQuery('delete', {id: idToDelete});
        deletePromise.then(row.remove())
            .catch(error => window.alert(error));
    }
}


/**
 * Swaps visibility of edit, delete and save buttons of given row
 */
function swapRowButtons(row) {
    if (row.querySelector('.edit .btn-save').style.display === 'none') {
        row.querySelector('.edit .btn-edit').style.display = 'none';
        row.querySelector('.edit .btn-delete').style.display = 'none';
        row.querySelector('.edit .btn-save').style.display = 'inline';
    } else {
        row.querySelector('.edit .btn-edit').style.display = 'inline';
        row.querySelector('.edit .btn-delete').style.display = 'inline';
        row.querySelector('.edit .btn-save').style.display = 'none';
    }
}


function saveShowNewValues(row) {
    row.querySelectorAll('[class^=col_]').forEach(field => {
        let newValue = field.querySelector('input, select').value;
        if (newValue !== null) {
            field.textContent = newValue;
        } else {
            field.textContent = field.getAttribute('temp');
        }
        field.removeAttribute('temp');
    });
}

function saveRestoreOldValues(row) {
    row.querySelectorAll('[class^=col_]').forEach(field => {
        field.textContent = field.getAttribute('temp');
        field.removeAttribute('temp');
    });
}

function saveMakeRequestBody(row) {
    let inputValues = {};
    row.querySelectorAll('[class^=col_]').forEach(field => {
        let inputE = field.querySelector('input, select');
        inputValues[inputE.name] = inputE.value;
    });
    inputValues['id'] = row.getAttribute('id');
    return inputValues
}

/**
 * Creates on-click function for list item save buttons
 */
function saveButtonCallback(row) {
    let requestBody = saveMakeRequestBody(row);
    let updatePromise = databaseQuery('edit', requestBody);
    updatePromise.then(() => {
        saveShowNewValues(row);
    })
        .catch(error => {
            console.log(error);
            saveRestoreOldValues(row);
        });
}



let knownTypes = [];

function getKnownTypes() {
    let types = [];
    document.querySelectorAll('#items_table tbody tr td.col_1').forEach(td => {
        let type = td.textContent;
        if (!(types.includes(type))) {
            types.push(td.textContent);
        }
    });
    knownTypes = types;
}

function makeTypeOptions(selectElement) {
    for (let optionType of knownTypes) {
        let newOption = document.createElement('option');
        newOption.setAttribute('value', optionType);
        newOption.textContent = optionType;
        selectElement.appendChild(newOption);
    }
}

// Hack
let columnNames = [
    'type', 'name', 'style', 'colour', 'comfy', 'sexy', 'mend', 'state'
];

/**
 * Creates inputs in place of table values.
 */
function editButtonCallback(row) {
    row.querySelectorAll('[class^=col_]').forEach(field => {
        let inputField;
        let fieldIndex = parseInt(field.getAttribute('class')[
            field.getAttribute('class').search(/col_[0-9]/) + 4
            ]) - 1;

        if (columnNames[fieldIndex] === 'type') {
            inputField = document.createElement('select');
            makeTypeOptions(inputField);
        } else {
            inputField = document.createElement('input');
            inputField.defaultValue = field.textContent;
        }
        inputField.setAttribute('name', columnNames[fieldIndex]);
         if (columnNames[fieldIndex] === 'sexy') {
             inputField.setAttribute('type', 'number');
         }
         field.setAttribute('temp', field.textContent);
         field.textContent = '';
        field.appendChild(inputField);
    });
}

function useButtonCallback(row) {
    let modal = document.querySelector('#usedModal');
    let modalTitle = modal.querySelector('.modal-title');
    modalTitle.textContent = row.querySelector('.Specimen').textContent;

    let modalSubTitle = modal.querySelector('.modal-subtitle');
    modalSubTitle.textContent = "[" +
        row.querySelector('.Colour').textContent + " | " +
        row.querySelector('.Type').textContent + "]";

    modal.querySelector('form input#item-id').value = row.id;
}

function useSaveButtonCallback() {
    let modal = document.querySelector('#usedModal');
    let itemId = modal.querySelector('form input#item-id').value;
    let itemDay = modal.querySelector('form input[name="use_day"]:checked').value;
    let requestBody = {
        'id': itemId,
        'day': itemDay,
    };
    if (itemDay === 'custom') {
        let selectedDate = modal.querySelector('form input#use-date').value;
        if (! selectedDate) {
            console.log('No date selected!!!');
            window.alert('No date selected!!!');
            return
        } else {
            requestBody['date'] = selectedDate;
        }
    }

    // $('#usedModal').modal('hide');
    let updatePromise = databaseQuery('use', requestBody);
    updatePromise.then(() => {
    })
        .catch(error => {
            console.log(error);
            window.alert(error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    getKnownTypes();  // Find known types on items load

    // Hide all save buttons
    let saveButtons = document.querySelectorAll('button.btn-save');
    saveButtons.forEach(btn => {
        btn.hidden = true;
    });

    // Set modal save button onclick
    let modal = document.querySelector('#usedModal');
    let modalSaveButton = modal.querySelector('.modal-footer .btn-used-save');
    modalSaveButton.onclick = () => {
        useSaveButtonCallback()
    };
});

window.operateEvents = {
    'click .btn-edit': (event) => {
        editButtonCallback(event.target.parentNode.parentNode);
        event.target.parentNode.querySelector('button.btn-save').hidden = false;
        event.target.hidden = true;
    },
    'click .btn-save': (event) => {
        saveButtonCallback(event.target.parentNode.parentNode);
        event.target.parentNode.querySelector('button.btn-edit').hidden = false;
        event.target.hidden = true;
    },
    'click .btn-delete': (event) => {
        deleteButtonCallback(event.target.parentNode.parentNode);
    },
        'click .btn-test': (event) => {
        useSaveButtonCallback(event);
    },
    'click .btn-used': (event) => {
        useButtonCallback(event.target.parentNode.parentNode);
    },

};
