
// once the DOM is loaded, run the main function
document.addEventListener('DOMContentLoaded', main);
function main () {

    document.getElementById("name-field").classList.remove("compressed");
    document.getElementById("name").focus(); 

    document.getElementById('name').addEventListener('keydown', (event) => { if (event.key === 'Enter') { 
            document.getElementById("workplace-field").classList.remove('compressed');
            document.getElementById("workplace").focus();
    }});

    document.getElementById('workplace').addEventListener('keydown', (event) => { if (event.key === 'Enter') { 
            document.getElementById("excitement-field").classList.remove('compressed');
            document.getElementById("excitement").focus();
    }});

    document.getElementById('excitement').addEventListener('input', (event) => {
        if (event.target.value.length > 0) { document.getElementById('form-submit').classList.remove('compressed'); } 
        else { document.getElementById('form-submit').classList.add('compressed'); }
    });

    document.getElementById('excitement').addEventListener('keydown', (event) => { if (event.key === 'Enter') { 
        document.getElementById('form-submit').focus();
    }});

    const textarea = document.getElementById('excitement');
    textarea.addEventListener('input', function() {
        while (textarea.scrollHeight > textarea.offsetHeight && textarea.rows < 20) { textarea.rows = textarea.rows + 1; }
        while (textarea.scrollHeight < textarea.offsetHeight) { textarea.rows = textarea.rows - 1; }
    });

    for (let evt of ["keydown", "click"]) { document.getElementById('form-submit').addEventListener(evt, async function(event) {

        if (evt == "keydown" && event.key !== 'Enter') { return }

        const response = await fetch('/submit', {
            method: 'POST',
            body: JSON.stringify({
                name: document.getElementById('name').value,
                workplace: document.getElementById('workplace').value,
                answer: document.getElementById('excitement').value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!(response.status == 200)) { return }
        const data = await response.json();
    
        document.getElementById('form').classList.add('compressed');
        document.getElementById('welcome-name').innerHTML = data.name;
        document.getElementById('welcome').classList.remove('compressed');

        console.log(data)
        document.body.style.backgroundColor = data.RGB;
    
    });}

}
