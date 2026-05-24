import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import WebGL from 'three/addons/capabilities/WebGL.js';

// WebGL checks for Chumi
if (!WebGL.isWebGL2Available()) {
    const status = document.querySelector("#status")
    status.innerHTML = "WebGL issue detected."
    status.appendChild(WebGL.getWebGL2ErrorMessage())
    throw new Error()
}

// Create all Three rendering objects
const canvas = document.querySelector("#canvas")
const camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000)

const scene = new THREE.Scene()
const renderGroup = new THREE.Group()

const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true })
renderer.setSize(canvas.clientWidth, canvas.clientHeight)
renderer.setPixelRatio(window.devicePixelRatio)
renderer.setAnimationLoop(animate)
renderer.setClearColor(0x222222)

const controls = new OrbitControls(camera, renderer.domElement)
controls.autoRotate = true
controls.cursorStyle = "grab"
controls.enableDamping = true

window.addEventListener("resize", () => {
    camera.aspect = canvas.clientWidth / canvas.clientHeight
    camera.updateProjectionMatrix()

    renderer.setSize(canvas.clientWidth, canvas.clientHeight)
})

var key = new THREE.Object3D()
renderGroup.add(key)

// Lights are camera based, not just in the scene
const light = new THREE.PointLight(0xFFFFFF, 2, 0, 0)
light.position.set(0, 0, 50)
camera.add(light)

const light2 = new THREE.PointLight(0xFFFFFF, 1, 0, 0)
light2.position.set(0, 0, -100)
camera.add(light2)

renderGroup.add(camera)
scene.add(renderGroup)

var lastTime = 0;
function animate(time) {
    var deltaTime = (time - lastTime) / 1000
    lastTime = time

    controls.update(deltaTime)
    renderer.render(scene, camera)
}

async function loadStl(file) {
    const stlLoader = new STLLoader()
    var geometry = await stlLoader.loadAsync(file)
    var brassMaterial = new THREE.MeshPhongMaterial({
        color: 0xE3BD7A,
        specular: 0xE3BD7A,
        shininess: 30
    })
    return new THREE.Mesh(geometry, brassMaterial)
}

export async function loadKey(file) {
    renderGroup.remove(key)
    if ("geometry" in key)
        key.geometry.dispose()
    if ("material" in key)
        key.material.dispose()
    key = await loadStl(file)

    key.geometry.computeBoundingBox()
    var boundingBox = key.geometry.boundingBox
    var center = new THREE.Vector3()
    boundingBox.getCenter(center)
    var boundedSize = boundingBox.max.sub(boundingBox.min)
    var size = boundedSize.length()

    key.translateX(-center.x)
    key.translateY(-center.y)
    key.pivot = center
    key.rotation.z = -Math.PI / 2

    camera.position.z = size * 0.75
    renderGroup.add(key)
}