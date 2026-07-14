import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import WebGL from 'three/addons/capabilities/WebGL.js';

const status = document.querySelector('#status');
const canvas = document.querySelector('#canvas');

if (!canvas) {
    throw new Error('The 3D preview canvas is missing.');
}

if (!WebGL.isWebGL2Available()) {
    const errorMessage = WebGL.getWebGL2ErrorMessage();
    if (status) {
        status.replaceChildren(document.createTextNode('WebGL 2 is required for the 3D preview. '), errorMessage);
    }
    throw new Error('WebGL 2 is not available.');
}

const MAX_DEVICE_PIXEL_RATIO = 2;
const scene = new THREE.Scene();
const renderGroup = new THREE.Group();
const camera = new THREE.PerspectiveCamera(42, 1, 0.01, 2000);
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

renderer.setClearColor(0x080b10, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.shadowMap.enabled = false;

const environment = new RoomEnvironment();
const environmentGenerator = new THREE.PMREMGenerator(renderer);
const environmentMap = environmentGenerator.fromScene(environment, 0.04).texture;
scene.environment = environmentMap;
environment.dispose();
environmentGenerator.dispose();

const controls = new OrbitControls(camera, renderer.domElement);
controls.autoRotate = false;
controls.cursorStyle = 'grab';
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.screenSpacePanning = true;
canvas.style.touchAction = 'pan-y';

scene.add(renderGroup);

const hemisphere = new THREE.HemisphereLight(0xeaf3ff, 0x2b1f18, 1.6);
const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
const fillLight = new THREE.DirectionalLight(0x9fc9ff, 1.35);
const rimLight = new THREE.DirectionalLight(0xffd4a3, 1.8);

keyLight.position.set(6, 8, 10);
fillLight.position.set(-8, 2, 5);
rimLight.position.set(3, -8, -6);
scene.add(hemisphere, keyLight, fillLight, rimLight);

let object = null;
let loadRevision = 0;
let lastFrameTime = null;
let rendering = false;
const viewDirections = {
    front: new THREE.Vector3(0, 0, 1),
    top: new THREE.Vector3(0, 1, 0.001),
    iso: new THREE.Vector3(0.82, 0.55, 1.25),
};

function cappedPixelRatio() {
    return Math.min(window.devicePixelRatio || 1, MAX_DEVICE_PIXEL_RATIO);
}

function disposeMesh(mesh) {
    if (!mesh) {
        return;
    }
    mesh.geometry?.dispose();
    if (Array.isArray(mesh.material)) {
        mesh.material.forEach((material) => material.dispose());
    } else {
        mesh.material?.dispose();
    }
}

function fitCameraToObject(mesh, viewDirection = viewDirections.iso) {
    const sphere = mesh?.geometry?.boundingSphere;
    if (!sphere) {
        return;
    }

    const radius = Math.max(sphere.radius, 0.01);
    const verticalFov = THREE.MathUtils.degToRad(camera.fov);
    const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * Math.max(camera.aspect, 0.01));
    const limitingFov = Math.max(Math.min(verticalFov, horizontalFov), THREE.MathUtils.degToRad(5));
    const distance = (radius / Math.sin(limitingFov / 2)) * 1.15;
    controls.target.set(0, 0, 0);
    camera.position.copy(viewDirection.clone().normalize().multiplyScalar(distance));
    camera.near = Math.max(0.01, distance - radius * 2.5);
    camera.far = Math.max(camera.near + 1, distance + radius * 5);
    camera.updateProjectionMatrix();
    camera.lookAt(controls.target);

    controls.minDistance = Math.max(radius * 0.15, 0.01);
    controls.maxDistance = Math.max(radius * 20, distance * 2);
    controls.update();
}

function updateViewSelection(activeView = '') {
    for (const view of ['front', 'top', 'iso']) {
        document.querySelector(`#view-${view}`)?.setAttribute('aria-pressed', String(view === activeView));
    }
}

export function fitView() {
    if (!object) {
        return;
    }
    const currentDirection = camera.position.clone().sub(controls.target);
    fitCameraToObject(object, currentDirection.lengthSq() ? currentDirection : viewDirections.iso);
    updateViewSelection();
}

export function setView(view) {
    if (!object || !(view in viewDirections)) {
        return;
    }
    fitCameraToObject(object, viewDirections[view]);
    updateViewSelection(view);
}

document.querySelector('#view-fit')?.addEventListener('click', fitView);
for (const view of ['front', 'top', 'iso']) {
    document.querySelector(`#view-${view}`)?.addEventListener('click', () => setView(view));
}

function resizeRenderer({ refit = true } = {}) {
    const bounds = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.round(bounds.width));
    const height = Math.max(1, Math.round(bounds.height));

    renderer.setPixelRatio(cappedPixelRatio());
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    if (refit && object) {
        fitCameraToObject(object);
    }
}

function animate(time) {
    const deltaTime = lastFrameTime === null ? 0 : Math.min((time - lastFrameTime) / 1000, 0.1);
    lastFrameTime = time;
    controls.update(deltaTime);
    renderer.render(scene, camera);
}

function startRendering() {
    if (rendering || document.hidden) {
        return;
    }
    lastFrameTime = null;
    renderer.setAnimationLoop(animate);
    rendering = true;
}

function stopRendering() {
    if (!rendering) {
        return;
    }
    renderer.setAnimationLoop(null);
    rendering = false;
    lastFrameTime = null;
}

function syncMotionPreference(event = reducedMotion) {
    if (event.matches) {
        controls.autoRotate = false;
    }
}

function syncTabs() {
    const relationships = [
        ['key-tab-button', 'key-tab'],
        ['follower-tab-button', 'follower-tab'],
    ];

    for (const [buttonId, panelId] of relationships) {
        const button = document.getElementById(buttonId);
        const panel = document.getElementById(panelId);
        if (!button || !panel) {
            continue;
        }

        const selected = !panel.classList.contains('hide');
        button.setAttribute('aria-selected', String(selected));
        button.tabIndex = selected ? 0 : -1;
        panel.setAttribute('aria-hidden', String(!selected));
        panel.inert = !selected;
    }
}

function enableTabKeyboardNavigation() {
    const tabList = document.querySelector('[role="tablist"]');
    if (!tabList) {
        return;
    }

    tabList.addEventListener('keydown', (event) => {
        const tabs = [...tabList.querySelectorAll('[role="tab"]')];
        const currentIndex = tabs.indexOf(document.activeElement);
        if (currentIndex < 0) {
            return;
        }

        let nextIndex = currentIndex;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
            nextIndex = (currentIndex + 1) % tabs.length;
        } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
            nextIndex = (currentIndex - 1 + tabs.length) % tabs.length;
        } else if (event.key === 'Home') {
            nextIndex = 0;
        } else if (event.key === 'End') {
            nextIndex = tabs.length - 1;
        } else {
            return;
        }

        event.preventDefault();
        tabs[nextIndex].focus();
        tabs[nextIndex].click();
    });
}

const tabPanels = [...document.querySelectorAll('[role="tabpanel"]')];
if (tabPanels.length) {
    const tabObserver = new MutationObserver(syncTabs);
    tabPanels.forEach((panel) => tabObserver.observe(panel, { attributes: true, attributeFilter: ['class'] }));
}

enableTabKeyboardNavigation();
syncTabs();
resizeRenderer({ refit: false });
startRendering();

if ('ResizeObserver' in window) {
    const resizeObserver = new ResizeObserver(() => resizeRenderer({ refit: false }));
    resizeObserver.observe(canvas);
} else {
    window.addEventListener('resize', () => resizeRenderer({ refit: false }), { passive: true });
}
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopRendering();
    } else {
        resizeRenderer({ refit: false });
        startRendering();
    }
});

if (typeof reducedMotion.addEventListener === 'function') {
    reducedMotion.addEventListener('change', syncMotionPreference);
} else {
    reducedMotion.addListener(syncMotionPreference);
}

window.addEventListener('pagehide', (event) => {
    stopRendering();
    if (!event.persisted) {
        disposeMesh(object);
        environmentMap.dispose();
        renderer.dispose();
    }
});

window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        resizeRenderer({ refit: false });
        startRendering();
    }
});

async function loadStl(file, roughness = 0.5, metalness = 0.5, color = 0xE3BD7A) {
    const geometry = await new STLLoader().loadAsync(file);
    if (!geometry.getAttribute('normal')) {
        geometry.computeVertexNormals();
    }
    geometry.computeBoundingBox();

    if (!geometry.boundingBox || geometry.boundingBox.isEmpty()) {
        geometry.dispose();
        throw new Error('The generated model has no visible geometry.');
    }

    const center = geometry.boundingBox.getCenter(new THREE.Vector3());
    geometry.translate(-center.x, -center.y, -center.z);
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();

    const material = new THREE.MeshStandardMaterial({
        color,
        roughness,
        metalness,
    });
    return new THREE.Mesh(geometry, material);
}

export async function loadObject(file, roughness = 0.5, metalness = 0.5, color = 0xE3BD7A) {
    const revision = ++loadRevision;
    const nextObject = await loadStl(file, roughness, metalness, color);

    if (revision !== loadRevision) {
        disposeMesh(nextObject);
        return;
    }

    nextObject.rotation.z = -Math.PI / 2;
    nextObject.updateMatrixWorld(true);

    if (object) {
        renderGroup.remove(object);
        disposeMesh(object);
    }

    object = nextObject;
    renderGroup.add(object);
    resizeRenderer({ refit: false });
    fitCameraToObject(object);
    updateViewSelection('iso');
}
