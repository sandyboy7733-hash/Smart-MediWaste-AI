const navItems = document.querySelectorAll(".nav-item");
const pages = document.querySelectorAll(".page");
const title = document.getElementById("pageTitle");

const titles = {
  dashboard: "Smart Medical Waste Monitoring",
  scanner: "AI Waste Scanner",
  collection: "Collection Management",
  analytics: "Waste Analytics",
  alerts: "System Alerts",
  settings: "System Settings"
};

function showPage(id) {
  pages.forEach(p =>
    p.classList.toggle("active-page", p.id === id)
  );

  navItems.forEach(n =>
    n.classList.toggle("active", n.dataset.page === id)
  );

  title.textContent = titles[id] || "MediWaste AI";

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
}

navItems.forEach(item => {
  item.addEventListener("click", () => {
    showPage(item.dataset.page);
  });
});


/* =========================================
   REAL LAPTOP CAMERA
========================================= */

let cameraStream = null;
let cameraRunning = false;

const scannerBtn = document.getElementById("scannerBtn");
const cameraText = document.getElementById("cameraText");
const cameraBox = document.querySelector(".camera");


async function startCamera() {

  try {

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert(
        "Your browser does not support camera access. Please use Chrome or Edge."
      );
      return;
    }

    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: {
          ideal: 1280
        },
        height: {
          ideal: 720
        },
        facingMode: "user"
      },
      audio: false
    });

    /* Create video element */

    let video = document.getElementById("cameraVideo");

    if (!video) {

      video = document.createElement("video");

      video.id = "cameraVideo";

      video.autoplay = true;
      video.playsInline = true;
      video.muted = true;

      video.style.position = "absolute";
      video.style.inset = "0";
      video.style.width = "100%";
      video.style.height = "100%";
      video.style.objectFit = "cover";
      video.style.zIndex = "0";

      cameraBox.prepend(video);
    }

    video.srcObject = cameraStream;

    cameraRunning = true;

    cameraText.textContent = "Camera Active";

    scannerBtn.textContent = "Stop Camera";

    document.querySelector(".camera small").textContent =
      "Live laptop camera feed";

    console.log("Camera started successfully.");

  } catch (error) {

    console.error("Camera error:", error);

    if (error.name === "NotAllowedError") {

      alert(
        "Camera permission was denied. Please allow camera access in your browser."
      );

    } else if (error.name === "NotFoundError") {

      alert(
        "No camera was found on this laptop."
      );

    } else {

      alert(
        "Unable to access the camera.\n\nError: " + error.message
      );
    }
  }
}


/* =========================================
   STOP CAMERA
========================================= */

function stopCamera() {

  if (cameraStream) {

    cameraStream.getTracks().forEach(track => {
      track.stop();
    });

    cameraStream = null;
  }

  const video = document.getElementById("cameraVideo");

  if (video) {
    video.remove();
  }

  cameraRunning = false;

  cameraText.textContent = "Camera Ready";

  scannerBtn.textContent = "Start Scanner";

  document.querySelector(".camera small").textContent =
    'Click "Start Scanner" to begin camera';
}


/* =========================================
   START / STOP BUTTON
========================================= */

scannerBtn.addEventListener("click", async function () {

  if (!cameraRunning) {

    this.disabled = true;

    await startCamera();

    this.disabled = false;

  } else {

    stopCamera();
  }

});


/* =========================================
   REFRESH BINS
========================================= */

document
  .getElementById("refreshBins")
  .addEventListener("click", function () {

    this.textContent = "✓ Updated";

    setTimeout(() => {
      this.textContent = "↻ Refresh";
    }, 1200);

  });


/* =========================================
   ADD DEMO COLLECTION RECORD
========================================= */

document
  .getElementById("addDemo")
  .addEventListener("click", function () {

    const id =
      "MW-" +
      String(Math.floor(Math.random() * 900) + 100);

    const now =
      new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
      });

    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${id}</td>
      <td>Glove</td>
      <td>
        <span class="pill infectious-pill">
          Infectious
        </span>
      </td>
      <td>Emergency</td>
      <td>${now}</td>
      <td>
        <span class="done">
          ● Collected
        </span>
      </td>
    `;

    document
      .getElementById("records")
      .prepend(row);

  });
  async function testCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        console.log("✅ Camera is working!");
        console.log("Camera stream:", stream);

        const video = document.createElement("video");
        video.srcObject = stream;
        video.autoplay = true;
        video.style.width = "500px";
        video.style.display = "block";

        document.body.appendChild(video);

    } catch (error) {
        console.error("❌ Camera error:", error);

        alert("Camera is NOT working: " + error.message);
    }
}


/* =========================================
   CLEANUP WHEN PAGE IS CLOSED
========================================= */

window.addEventListener("beforeunload", () => {

  if (cameraStream) {

    cameraStream.getTracks().forEach(track => {
      track.stop();
    });

  }

});