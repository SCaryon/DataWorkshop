class MeshLine {
    constructor(options) {
        let baseDef = {
            lineWidth: 1,
            resolution: [1, 1],
            map: null,
            color: 0xffffff,
            useMap: false,
            depthTest: true,
            transparent: false,
            opacity: 1,
            wireframe: false
        }
        this.initions = Object.assign(baseDef, options)
        return this
    }

    setGeometry(geometry, thick) {
        let meshGeom = this.createGeometry(geometry)
        let material = this.createMaterial()

        this.mesh = new THREE.Mesh(meshGeom, material)
        return this.mesh
    }

    createMaterial() {
        let materialConf = this.initions
        let uniforms = {
            resolution: {value: new THREE.Vector2(...materialConf.resolution)},
            uColor: {value: new THREE.Color(materialConf.color)},
            map: {value: null},
            useMap: {value: materialConf.useMap},
            width: {value: materialConf.lineWidth},
            opacity: {value: materialConf.opacity}
        }
        if (materialConf.map) {
            uniforms.map.value = new THREE.TextureLoader().load(materialConf.map)
        }
        return new THREE.ShaderMaterial({
            uniforms,
            vertexShader: document.getElementById('vertexShader').textContent,
            fragmentShader: document.getElementById('fragmentShader').textContent,
            side: THREE.DoubleSide,
            depthTest: materialConf.depthTest,
            transparent: materialConf.transparent
        })
    }

    createGeometry(geometry) {
        let verticesCount = geometry.vertices.length
        let bufferGeometry = new THREE.PlaneBufferGeometry(0, 0, 1, verticesCount - 1)
        let prevPositions = new Float32Array(verticesCount * 3 * 2)
        let nextPositions = new Float32Array(verticesCount * 3 * 2)
        let side = new Float32Array(verticesCount * 2)
        let uv = bufferGeometry.attributes.uv.array
        let position = bufferGeometry.attributes.position.array
        for (let j = 0; j < verticesCount * 2; j += 2) {
            let ratio = j / (verticesCount - 1) / 2

            // side
            side[j] = 1
            side[j + 1] = -1

            // index
            let current = geometry.vertices[j / 2]
            let prev = geometry.vertices[(j === 0 ? j : j - 2) / 2]
            let next = geometry.vertices[(j === (verticesCount - 1) * 2 ? j : j + 2) / 2]
            // position
            position[j * 3] = current.x
            position[j * 3 + 1] = current.y
            position[j * 3 + 2] = current.z
            position[j * 3 + 3] = current.x
            position[j * 3 + 4] = current.y
            position[j * 3 + 5] = current.z

            // prev
            prevPositions[j * 3] = prev.x
            prevPositions[j * 3 + 1] = prev.y
            prevPositions[j * 3 + 2] = prev.z
            prevPositions[j * 3 + 3] = prev.x
            prevPositions[j * 3 + 4] = prev.y
            prevPositions[j * 3 + 5] = prev.z

            // next
            nextPositions[j * 3] = next.x
            nextPositions[j * 3 + 1] = next.y
            nextPositions[j * 3 + 2] = next.z
            nextPositions[j * 3 + 3] = next.x
            nextPositions[j * 3 + 4] = next.y
            nextPositions[j * 3 + 5] = next.z

            uv[j * 2] = ratio
            uv[j * 2 + 2] = ratio
            uv[j * 2 + 1] = 0
            uv[j * 2 + 3] = 1
        }

        bufferGeometry.addAttribute('prevPositions', new THREE.BufferAttribute(prevPositions, 3))
        bufferGeometry.addAttribute('nextPositions', new THREE.BufferAttribute(nextPositions, 3))
        bufferGeometry.addAttribute('side', new THREE.BufferAttribute(side, 1))
        return bufferGeometry
    }
}

class GeoMeshLine extends THREE.Object3D {
    constructor(geojson, matConf) {
        super()
        this.matcConf = matConf
        let features = geojson.features
        features.forEach(ft => {
            if (ft.geometry.type === 'Polygon') {
                this.draw(ft.geometry.coordinates[0])
            } else if (ft.geometry.type === 'MultiPolygon') {
                ft.geometry.coordinates.forEach((cd) => {
                    this.draw(cd[0])
                })
            }
        })
    }

    draw(points) {
        let geometry = new THREE.Geometry()
        points.forEach((lnglat) => {
            let vec = new THREE.Vector3(...lnglat)
            geometry.vertices.push(vec)
        })
        let meshline = new MeshLine(this.matcConf).setGeometry(geometry)
        this.add(meshline)
    }
}

var camera, scene, controls, geoMeshline

function run() {
    init();
    initMeshLine();
    render();
}

function init() {
    var SCREEN_WIDTH = window.innerWidth, SCREEN_HEIGHT = window.innerHeight
    renderer = new THREE.WebGLRenderer({
        antialias: true
    });
    renderer.setSize(SCREEN_WIDTH, SCREEN_HEIGHT);
    document.getElementById('ThreeJS').appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(45, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 1000);
    camera.position.z = 500;
    controls = new THREE.TrackballControls(camera);

    scene = new THREE.Scene()
}

function initMeshLine() {
    fetch('https://raw.githubusercontent.com/apache/incubator-echarts/2.2.7/doc/example/geoJson/continent_geo.json')
        .then(res => res.json())
        .then(res => {
            geoMeshline = new GeoMeshLine(res, {
                resolution: [window.innerWidth, window.innerHeight],
                color: 0x00ffff,
                lineWidth: 2
            })
            scene.add(geoMeshline)
        })
}

function render() {
    renderer.render(scene, camera);
    controls.update()
    // if (geoMeshline) {
    //   geoMeshline.rotation.y += 0.01
    // }
    requestAnimationFrame(render);
}

run()