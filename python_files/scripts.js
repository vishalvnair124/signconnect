// Core variables
let scene,
  renderer,
  camera,
  model,
  neck,
  waist,
  possibleAnims,
  mixer,
  idle,
  clock = new THREE.Clock(),
  currentlyAnimating = false,
  raycaster = new THREE.Raycaster(),
  loaderAnim = document.getElementById("js-loader");

init();
update();
window.addEventListener("click", (e) => raycast(e));
window.addEventListener("touchend", (e) => raycast(e, true));

function init() {
  const MODEL_PATH =
    "https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy_lightweight.glb";
  const canvas = document.querySelector("#c");
  const backgroundColor = 0xf1f1f1;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(backgroundColor);
  scene.fog = new THREE.Fog(backgroundColor, 60, 100);

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.shadowMap.enabled = true;
  renderer.setPixelRatio(window.devicePixelRatio);
  document.body.appendChild(renderer.domElement);

  camera = new THREE.PerspectiveCamera(
    50,
    window.innerWidth / window.innerHeight,
    0.11
  );
  camera.position.set(0, -3, 30);

  const stacy_txt = new THREE.TextureLoader().load(
    "https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy.jpg"
  );
  stacy_txt.flipY = false;
  const stacy_mtl = new THREE.MeshPhongMaterial({
    map: stacy_txt,
    color: 0xffffff,
    skinning: true,
  });

  const loader = new THREE.GLTFLoader();
  loader.load(
    MODEL_PATH,
    (gltf) => {
      model = gltf.scene;
      let fileAnimations = gltf.animations;

      model.traverse((o) => {
        if (o.isMesh) {
          o.castShadow = true;
          o.receiveShadow = true;
          o.material = stacy_mtl;
        }
        if (o.isBone && o.name === "mixamorigNeck") neck = o;
        if (o.isBone && o.name === "mixamorigSpine") waist = o;
      });

      model.scale.set(7, 7, 7);
      model.position.y = -11;
      scene.add(model);
      loaderAnim.remove();

      const clips = fileAnimations.filter((val) => val.name !== "idle");
      mixer = new THREE.AnimationMixer(model);
      possibleAnims = clips.map((val) => {
        let clip = THREE.AnimationClip.findByName(clips, val.name);
        clip.tracks.splice(3, 3);
        clip.tracks.splice(9, 3);
        return mixer.clipAction(clip);
      });

      const idleAnim = THREE.AnimationClip.findByName(fileAnimations, "idle");
      idleAnim.tracks.splice(3, 3);
      idleAnim.tracks.splice(9, 3);
      idle = mixer.clipAction(idleAnim);
      idle.play();
    },
    undefined,
    console.error
  );

  const hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.61);
  hemiLight.position.set(0, 50, 0);
  scene.add(hemiLight);

  const dirLight = new THREE.DirectionalLight(0xffffff, 0.54);
  dirLight.position.set(-8, 12, 8);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(1024, 1024);
  const d = 8.25;
  dirLight.shadow.camera.near = 0.1;
  dirLight.shadow.camera.far = 1500;
  dirLight.shadow.camera.left = -d;
  dirLight.shadow.camera.right = d;
  dirLight.shadow.camera.top = d;
  dirLight.shadow.camera.bottom = -d;
  scene.add(dirLight);

  const floorGeometry = new THREE.PlaneGeometry(5000, 5000, 1, 1);
  const floorMaterial = new THREE.MeshPhongMaterial({
    color: 0xeeeeee,
    shininess: 0,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.rotation.x = -Math.PI * 0.5;
  floor.receiveShadow = true;
  floor.position.y = -11;
  scene.add(floor);

  const geometry = new THREE.SphereGeometry(8, 32, 32);
  const material = new THREE.MeshBasicMaterial({ color: 0x9bffaf });
  const sphere = new THREE.Mesh(geometry, material);
  sphere.position.set(-0.25, -2.5, -15);
  scene.add(sphere);
}

function update() {
  if (mixer) mixer.update(clock.getDelta());
  if (resizeRendererToDisplaySize(renderer)) {
    const canvas = renderer.domElement;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
  }
  renderer.render(scene, camera);
  requestAnimationFrame(update);
}

function resizeRendererToDisplaySize(renderer) {
  const canvas = renderer.domElement;
  const width = window.innerWidth;
  const height = window.innerHeight;
  const pixelWidth = canvas.width / window.devicePixelRatio;
  const pixelHeight = canvas.height / window.devicePixelRatio;
  const needResize = pixelWidth !== width || pixelHeight !== height;
  if (needResize) renderer.setSize(width, height, false);
  return needResize;
}

function raycast(e, touch = false) {
  const mouse = {};
  if (touch) {
    mouse.x = 2 * (e.changedTouches[0].clientX / window.innerWidth) - 1;
    mouse.y = 1 - 2 * (e.changedTouches[0].clientY / window.innerHeight);
  } else {
    mouse.x = 2 * (e.clientX / window.innerWidth) - 1;
    mouse.y = 1 - 2 * (e.clientY / window.innerHeight);
  }
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);
  if (intersects[0]) {
    const object = intersects[0].object;
    if (object.name === "stacy" && !currentlyAnimating) {
      currentlyAnimating = true;
      playOnClick();
    }
  }
}

function playOnClick() {
  const animIndex = Math.floor(Math.random() * possibleAnims.length);
  playModifierAnimation(idle, 0.25, possibleAnims[animIndex], 0.25);
}

function playModifierAnimation(from, fSpeed, to, tSpeed) {
  to.setLoop(THREE.LoopOnce);
  to.reset();
  to.play();
  from.crossFadeTo(to, fSpeed, true);
  setTimeout(() => {
    from.enabled = true;
    to.crossFadeTo(from, tSpeed, true);
    currentlyAnimating = false;
  }, to._clip.duration * 1000 - (tSpeed + fSpeed) * 1000);
}

document.addEventListener("mousemove", (e) => {
  const mousecoords = getMousePos(e);
  if (neck && waist) {
    moveJoint(mousecoords, neck, 50);
    moveJoint(mousecoords, waist, 30);
  }
});

function getMousePos(e) {
  return { x: e.clientX, y: e.clientY };
}

function moveJoint(mouse, joint, degreeLimit) {
  const deg = getMouseDegrees(mouse.x, mouse.y, degreeLimit);
  joint.rotation.y = THREE.Math.degToRad(deg.x);
  joint.rotation.x = THREE.Math.degToRad(deg.y);
}

function getMouseDegrees(x, y, degreeLimit) {
  const w = { x: window.innerWidth, y: window.innerHeight };
  let dx = 0,
    dy = 0,
    xdiff,
    xPercent,
    ydiff,
    yPercent;

  if (x <= w.x / 2) {
    xdiff = w.x / 2 - x;
    xPercent = (xdiff / (w.x / 2)) * 100;
    dx = ((degreeLimit * xPercent) / 100) * -1;
  }
  if (x >= w.x / 2) {
    xdiff = x - w.x / 2;
    xPercent = (xdiff / (w.x / 2)) * 100;
    dx = (degreeLimit * xPercent) / 100;
  }
  if (y <= w.y / 2) {
    ydiff = w.y / 2 - y;
    yPercent = (ydiff / (w.y / 2)) * 100;
    dy = ((degreeLimit * 0.5 * yPercent) / 100) * -1;
  }
  if (y >= w.y / 2) {
    ydiff = y - w.y / 2;
    yPercent = (ydiff / (w.y / 2)) * 100;
    dy = (degreeLimit * yPercent) / 100;
  }
  return { x: dx, y: dy };
}
