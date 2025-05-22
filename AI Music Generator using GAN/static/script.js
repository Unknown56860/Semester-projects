let selectedModel = "";

document.querySelectorAll("#modelList li").forEach(function(item) {
    item.addEventListener("click", function() {
        document.querySelectorAll("#modelList li").forEach(li => li.classList.remove("selected"));
        this.classList.add("selected");
        selectedModel = this.getAttribute("data-model");
    });
});

document.getElementById("generateBtn").addEventListener("click", function () {
    if (!selectedModel) {
        alert("Please select a model first.");
        return;
    }

    const button = this;
    button.disabled = true;
    button.textContent = "Generating...";

    fetch('/generate_music', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model: selectedModel })
    })
    .then(response => response.json())
    .then(data => {
        updateGeneratedMusicList(data.generatedFiles);
    })
    .catch(error => console.error("Error generating music:", error))
    .finally(() => {
        button.disabled = false;
        button.textContent = "Generate Music";
    });
});

function updateGeneratedMusicList(files) {
    const generatedMusicList = document.getElementById("generatedMusicList");

    files.forEach(file => {
        const exists = Array.from(generatedMusicList.children).some(
            li => li.getAttribute("data-file") === file
        );
        if (exists) return;

        const li = document.createElement("li");
        li.textContent = file;
        li.setAttribute("data-file", file);

        li.addEventListener("click", function () {
            document.querySelectorAll("#generatedMusicList li").forEach(li => li.classList.remove("selected"));
            this.classList.add("selected");
        });

        generatedMusicList.appendChild(li);
    });
}

function playSelectedMidi(fileName) {
    const filePath = `/music/${fileName}`;

    const midiPlayer = document.getElementById("midiPlayer");
    const midiVisualizer = document.getElementById("myVisualizer");

    midiPlayer.src = filePath;
    midiVisualizer.src = filePath;

    setTimeout(() => {
        if (midiPlayer && typeof midiPlayer.play === 'function') {
            midiPlayer.play();
        } else {
            console.warn("midiPlayer.play() not available");
        }
    }, 500);
}

document.getElementById("playBtn").addEventListener("click", function() {
    const selectedMusicFile = document.querySelector("#generatedMusicList li.selected");

    if (!selectedMusicFile) {
        alert("Please select a music file first.");
        return;
    }

    const file = selectedMusicFile.getAttribute("data-file");
    playSelectedMidi(file);
});
