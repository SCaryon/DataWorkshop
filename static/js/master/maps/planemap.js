var camera, scene, renderer;
window.onload = function () {
    var clock = new THREE.Clock();
    var keyboard = new THREEx.KeyboardState();
    var UserInterface = null;
    var Labels = null;
    var parseURL = new URLparser();
    var dollars = 100000000;//0.1billion
    var particles = 1000;
    var destination = [];
    var increment = 5;//点的位置变化增量
    var contrast = false;
    var percentage = 1;
    var loaded = false;//是否加载完毕
    var zoomlock = false;//禁止改变地图比例
    var selectedID = 0;//当前选中的节点（hover即选中）
    var shape = null;//存储plane的边界信息
    var products = {};//存储产品，包括atlasid，color，id,name,sales,x,x3,y,y3,z3
    var countries = {};
    var trades = {};
    var countryOverlay = null;//鼠标覆盖的地图的边界
    var links;//点云中的线
    var globeSize = 150;
    var names = [];//存储的是一个country中对应的一个点
    var countryIndex = 0;
    var categories = {};//下面的颜色目录条的信息
    var previousMode = "2D";//2D or 3D mode
    var darkMode = true;
    var cameraSpeed = 5;
    var selectedCountry = null;
    var currentSetup;//当前模式（也就是当前页面）
    var cameraControls = null;
    var isDragging = false, isClicking = false;
    var mouseCoord = {"x": 0, "y": 0};
    var currentZoom = 0;
    var filterCountry = null;//被选中的国家
    var constantSize = false;
    var Particlelinks = null;
    var particlesPlaced = 0;//被安置好的点的数量
    var overlayMaterial = null;

    //此方法在noWebGL.js里面，检测浏览器的可行性
    init();
    animate();
    existstory();

    /**
     * 初始化，设置camera，renderer，scene等
     * 载入data，包括边界、国家和产品信息
     * 增加一些监听动作
     */
    function init() {
        var WIDTH = window.innerWidth,
            HEIGHT = window.innerHeight;

        // set some camera attributes
        var VIEW_ANGLE = 45,
            ASPECT = WIDTH / HEIGHT,
            NEAR = 0.1,
            FAR = 10000;

        renderer = new THREE.WebGLRenderer();
        if (darkMode)
            renderer.setClearColor(0x000000, 1);
        else
            renderer.setClearColor(0xffffff, 1);

        camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);

        window.addEventListener('resize', function () {
            var WIDTH = window.innerWidth,
                HEIGHT = window.innerHeight;
            renderer.setSize(WIDTH, HEIGHT);
            camera.aspect = WIDTH / HEIGHT;
            camera.updateProjectionMatrix();
        });

        scene = new THREE.Scene();

        // add the camera to the scene
        scene.add(camera);
        //FogExp2对象的构造函数.用来在场景内创建指数雾效,指数雾效是雾效浓度递增根据指数(参数density)设定
        if (darkMode)
            scene.fog = new THREE.FogExp2(0xffffff, 0.001);
        else
            scene.fog = new THREE.FogExp2(0x00ffff, 0.001);

        camera.position.z = 450;

        renderer.setSize(window.innerWidth, window.innerHeight);


        UserInterface = new UI();
        UserInterface.addSpinner();

        document.body.appendChild(renderer.domElement);


        var attributes = {
            size: {type: 'f', value: null},
            customColor: {type: 'c', value: null},
        };

        var textureblock = new THREE.TextureLoader().load("/static/images/master/block.png");
        var uniforms = {
            color: {type: "c", value: new THREE.Color(0xffffff)},
            texture: {type: "t", value: textureblock}
        };
        var shaderMaterial = new THREE.ShaderMaterial({
            uniforms: uniforms,
            vertexShader: document.getElementById('vertexshader').textContent,
            fragmentShader: document.getElementById('fragmentshader').textContent,
        });

        geometry = new THREE.BufferGeometry();


        var color = new THREE.Color();
        var tetha, phi, ray = 3000;
        var v = 0;
        var totalTrade = 0;
        var count = 0;
        countryIndex = 0;
        var countryHTML = "";
        var planeShapeIDs;

        //载入边界信息
        $.getJSON("/static/data/master/world.json", function (json) {
            var texturecolormap = new THREE.TextureLoader().load("/static/images/master/colormap5.png");
            overlayMaterial = new THREE.MeshPhongMaterial({//一种光亮表面的材质效果
                map: texturecolormap,
                transparent: true,
                opacity: 0.5,
                blending: THREE.AdditiveBlending//决定物体如何与背景进行融合,提供一种半透明的眩光。
            });

            temp = drawThreeGeo(json, 400, 'plane', scene, {
                color: 0x7e7e7e,
                linewidth: 1,
                transparent: true,
                opacity: 0.7
            });
            shape = new THREE.Object3D();
            shape.add(temp[0]);//边界线
            overlay = new THREE.Mesh(new THREE.PlaneGeometry(560, 280, 1, 1), overlayMaterial);
            shape.add(overlay);
            planeShapeIDs = temp[1];//边界线ID

            // geoMeshline = new GeoMeshLine(json, {
            //     resolution: [window.innerWidth, window.innerHeight],
            //     color: 0x00ffff,
            //     lineWidth: 2
            // });
            // scene.add(geoMeshline);

            renderer.render(scene, camera);
        });


        /*在countries.json文件里面包含了四个主要信息：
        载入country，trade，categories，和products*/
        $.getJSON("/static/data/master/countries.json", function (corejson) {
            $.each(corejson.countries, function (co, country) {
                countries[co] = country;
            });
            $.each(planeShapeIDs, function (shapeid, shapes) {
                if (countries[shapeid])
                    countries[shapeid]["polygons"] = planeShapeIDs[shapeid];
            });
            $.each(corejson.products, function (pid, product) {
                products[pid] = product;
            });
            $.each(corejson.categories, function (cid, cat) {
                categories[cid] = cat;
            });
            Labels = new LabelManager(countries);

            UserInterface.buildCategories(categories);

            $.each(corejson.trade, function (i, val) {
                if (countries[i]) {
                    trades[i] = val;
                }
            });

            UserInterface.createSelectionBox(countries);


            countryIndex = 124;
            particles = 153726;
            var positions = new Float32Array(particles * 3);
            destination = new Float32Array(particles * 3);
            var values_color = new Float32Array(particles * 3);
            var values_size = new Float32Array(particles);
            var total = 0, v = 0, ray = 4, tetha = 0;

            for (var i = 0; i < countryIndex; i++) {
                //对每个index寻找相应的country
                $.each(countries, function (p, v) {
                    if (i == v.id) {
                        val = v;//country的属性们
                        code = p;//country的index
                    }
                });

                //找到countries中对应的国家后开始进行处理
                for (var key in val["products"]) {
                    productValue = val["products"][key];//键为key的product的量
                    productInfo = products[key];//键为key的product的具体信息

                    color = new THREE.Color(productInfo.color);

                    //在点集中加入点并设置它的位置、目标、大小、颜色的初值
                    for (var s = 0; s < Math.round(productValue / dollars); s++) {
                        names.push({"n": key, "c": code});
                        values_size[v] = 3;
                        values_color[v * 3 + 0] = color.r * 1.2;
                        values_color[v * 3 + 1] = color.g * 1.2;
                        values_color[v * 3 + 2] = color.b * 1.2;
                        destination[v * 3 + 0] = 1;
                        destination[v * 3 + 1] = 2;
                        destination[v * 3 + 2] = 5000;
                        positions[v * 3 + 0] = 1;
                        positions[v * 3 + 1] = 2;
                        positions[v * 3 + 2] = 5000;
                        v++;
                    }
                }
            }

            //geometry初始化后第一次变化
            geometry.addAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.addAttribute('customColor', new THREE.BufferAttribute(values_color, 3));
            geometry.addAttribute('size', new THREE.BufferAttribute(values_size, 1));
            geometry.addAttribute('attributes', new THREE.BufferAttribute(attributes, 1));

            particleSystem = new THREE.Points(geometry, shaderMaterial);
            particleSystem.frustrumCulled = true;
            scene.add(particleSystem);
            loaded = true;
            switcher("gridmap", false, 3);
            Particlelinks = new ParticleLinks(13000, clock, darkMode);
            links = Particlelinks.getMesh();
            scene.add(links);

            $(".countrySelection").on("change", function () {
                targetCountry($(this).val(), true, true);
                filterCountry = $(this).val();
            });


            $("#loaded").fadeOut();
            $("#spinner").fadeOut('slow');
            $('#choice').fadeIn('slow');
        });

        renderer.domElement.addEventListener("mousemove", mouseMove);
        renderer.domElement.addEventListener("mousedown", mouseDown);

        //定义各个监听事件
        window.addEventListener("mouseup", function () {
            //如果不是拖拽，那么鼠标抬起的时候将所有选中的移除并删除link
            if (!isDragging) {
                hideLinks();
                Labels.resetLabels(countries, darkMode);
            }
            UserInterface.changeCursor("default");
            isClicking = false;
            isDragging = false;
        });
        renderer.domElement.addEventListener("mousewheel", mousewheel, false);
        renderer.domElement.addEventListener("onmousewheel", mousewheel, false);
        //包括IE6在内的浏览器是使用onmousewheel，而FireFox浏览器一个人使用DOMMouseScroll
        renderer.domElement.addEventListener('DOMMouseScroll', mousewheel, false);
        $(renderer.domElement).dblclick(function (e) {
            if (previousMode === "2D") {
                cameraControls.zoom(10);
            }
        });

        if (darkMode)
            scene.add(new THREE.AmbientLight(0xFFFFFF));//环境光
        else
            scene.add(new THREE.AmbientLight(0x000000));//环境光

        zoomlock = false;
        cameraControls = new Controls(renderer.domElement, 450);
    }


    //这是点击一个国家以后触发的动作，给选择的国家连上相应type的线
    function addLinks(type, chosenCountry) {
        scene.remove(links);
        //links=new THREE.Object3D();
        var count = 0;
        var height = 15;
        var color = new THREE.Color();
        //大洲中心的坐标
        var continentCentroid = {
            1: [3.16, 19.33],
            2: [48.92, 85.78],
            3: [-13.58, 121.64],
            4: [53.12, 4.21],
            5: [-16.63, -59.76],
            6: [35.74, -102.3],
            7: [27.99, -173.32]
        };
        var regionCoords = [[-2.88891, 38.91750], [-3.23997, 18.52688], [26.98997, 16.41750], [-28.98956, 22.39406], [9.71916, -1.16062], [19.23786, -71.12156], [17.23455, -92.91844], [-24.91700, -58.46531], [44.28401, -99.24656], [41.97528, 68.44875], [35.96852, 120.12844], [29.77328, 68.44875], [-0.07764, 109.23000], [28.54528, 39.97219], [56.71013, 42.08156], [60.02608, 3.05813], [39.85016, 4.46438], [47.22653, 3.40969], [-33.20254, 144.73781], [-10.56414, 155.98781], [3.78679, 169.69875], [13.16436, 193.95656]];

        //为其他国家设置不透明度0，选中国家不透明度100
        $.each(countries, function (c, co) {
            if (darkMode)
                $("#" + c).css({'font-size': 10, 'color': '#FFFFFF', 'z-index': 2, 'opacity': 0});
            else
                $("#" + c).css({'font-size': 10, 'color': '#000000', 'z-index': 2, 'opacity': 0});

        });
        if (chosenCountry)
            if (darkMode)
                $("#" + chosenCountry).css({
                    'font-size': 24,
                    'color': '#FFFFFF',
                    'z-index': 4,
                    'opacity': 1
                });
            else
                $("#" + chosenCountry).css({
                    'font-size': 24,
                    'color': '#000000',
                    'z-index': 4,
                    'opacity': 1
                });

        var cartx, carty, cartz, cartx2, carty2, cartz2;
        $.each(trades, function (i, exports) {//对每个国家的出口
            country = countries[i];
            states = anchors[i];

            if (country && states) {
                var coord1 = continentCentroid[country.continent], coord2 = null;
                $.each(exports, function (j, val) {//对当前国家的每一个出口
                    country2 = countries[val.c];
                    if (country2 && (chosenCountry === "ALL" || chosenCountry === i)) {

                        if (darkMode)
                            $("#" + val.c).css({
                                'font-size': 12 + Math.sqrt(val.e) / 40,//字体大小和出口量有关
                                'color': '#eee',
                                'z-index': 2,
                                'opacity': 1
                            });
                        else
                            $("#" + val.c).css({
                                'font-size': 12 + Math.sqrt(val.e) / 40,//字体大小和出口量有关
                                'color': '#000',
                                'z-index': 2,
                                'opacity': 1
                            });
                        var coord2 = continentCentroid[country2.continent];
                        var segments = [];

                        var lon1 = Math.min(country.lat, country2.lat) / 180 * Math.PI;  // In radian
                        var lon2 = Math.max(country.lat, country2.lat) / 180 * Math.PI;  // In radian
                        var lat1 = Math.min(country.lon, country2.lon) / 180 * Math.PI; // In radian
                        var lat2 = Math.max(country.lon, country2.lon) / 180 * Math.PI; // In radian

                        var dLon = (lon2 - lon1);

                        var Bx = Math.cos(lat2) * Math.cos(dLon);
                        var By = Math.cos(lat2) * Math.sin(dLon);
                        var avgLat = Math.atan2(
                            Math.sin(lat1) + Math.sin(lat2),
                            Math.sqrt((Math.cos(lat1) + Bx) * (Math.cos(lat1) + Bx) + By * By));
                        avgLat = avgLat * 180 / Math.PI;
                        var avgLong = lon1 + Math.atan2(By, Math.cos(lat1) + Bx) * 180 / Math.PI;

                        //如果是二维的就提供首尾两点，三维的需要好几个点来确定一条曲线
                        height = 0;
                        color.setHSL(1, 1, 1);
                        segments.push(new THREE.Vector3(country2.lat * 1.55, country2.lon * 1.55, height));
                        segments.push(new THREE.Vector3(country.lat * 1.55, country.lon * 1.55, height));

                        line = Spline(segments, color.getHex(), 5 - j / 2);//返回一条线
                        Particlelinks.assignPositions(line.geometry.vertices, j, val.e);
                        //links.add(line);
                        if (chosenCountry === "ALL") return false;
                    }

                });
            }
        });

        links = Particlelinks.getMesh();
        scene.add(links);

    }

    //在三维的空间里画线
    function Spline(controlPoints, colorHex, width) {
        var numPoints = 40;

        var material = new THREE.LineDashedMaterial({
            dashSize: 1,
            gapSize: 100,
            // colorHex: colorHex,
            transparent: true,
            opacity: 0.8,
            vertexColors: true,
            linewidth: width + 1
        });
        var colors = [];
        var spline = new THREE.CatmullRomCurve3(controlPoints);//通过一系列的点来创建一条平滑的曲线。
        var geometry = new THREE.Geometry();
        var splinePoints = spline.getPoints(100);
        for (var i = 0; i < splinePoints.length; i++) {
            geometry.vertices.push(splinePoints[i]);
            colors[i] = new THREE.Color();
            colors[i].setHSL(0.5, 0.2, i / 100);//色相、饱和度、透明度
        }
        geometry.colors = colors;

        return (new THREE.Line(geometry, material, THREE.LineSegments));
    }

    //？？？？对于粒子系统
    function animateLinks() {
        Particlelinks.animate();

    }

    //在非产品空间移除连线
    function hideLinks() {
        scene.remove(links);
    }


    /*针对各种鼠标移动做出的反应
    * 关闭鼠标move的默认行为
    * 如果鼠标正在拖拽，那么对3D或者塔状的进行视线center的改变
    * 如果不是拖拽，那么对于非story状态，就需要确定当前鼠标是否触碰到了粒子系统中
    * 的任何粒子，找到触碰的最近的粒子，用label显示这个粒子的信息，查找粒子属于的国家
    * 然后将这个国家边界高亮*/
    function mouseMove(e) {
        /*pageX/pageY:鼠标相对于整个网页HTML页面的X/Y坐标。IE不适用
          clientX/clientY：事件发生时鼠标在浏览器内容区域的X/Y坐标（不包含滚动条）。
          screenX/screenY:鼠标在屏幕上的坐标。
          offsetX/offsetY:得出的结果跟pageX/pageY一样，IE专用*/
        moveY = (e.clientY || e.pageY);
        moveX = (e.clientX || e.pageX);
        e.preventDefault();//阻止元素发生默认的行为（例如，当点击提交按钮时阻止对表单的提交）。
        isDragging = isClicking;

        //如果是鼠标拖拽
        if (isDragging) {
            UserInterface.changeCursor("grabbing", cameraControls.isLocked());
            mouseCoord.x = moveX;
            mouseCoord.y = moveY;

            //如果不是拖拽，且不是在story模式
        } else if (loaded) {
            var mouseX = e.clientX / window.innerWidth * 2 - 1;
            var mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
            vector = new THREE.Vector3(mouseX, mouseY, 0);
            var values_color = geometry.attributes.customColor.array;
            var i = 1e3;
            var s = new THREE.Projector;//可以用来进行碰撞检测
            //Raycasting is used for mouse picking (working out what objects in the 3d space the mouse is over) amongst other things.
            var o = new THREE.Raycaster;
            cameraDistance = 3000;
            vector.unproject(camera);
            o.ray.set(camera.position, vector.sub(camera.position).normalize());

            intersects = o.intersectObject(particleSystem);//从中心点发射线与别的物品相交点从近到远的一个数组
            if (intersects.length > 0) {//如有相交
                for (var u = 0; u < intersects.length; u++) {//最近的相交物品
                    if (intersects[u].distanceToRay < i) {
                        i = intersects[u].distanceToRay;
                        //获取该国家的index
                        if (this.INTERSECTED != intersects[u].index && intersects[u].distance < cameraDistance - globeSize / 5) {
                            this.INTERSECTED = intersects[u].index;
                        }
                    }
                }
            } else if (this.INTERSECTED !== null) {
                this.INTERSECTED = null;
                highLightCountry(null, false);
            }

            if (this.INTERSECTED) {
                if (selectedID !== this.INTERSECTED) {
                    selectedID = this.INTERSECTED;
                }
                UserInterface.changeCursor("pointer");
                $("#pointer").css({left: e.pageX + 15, top: e.pageY - 7});
                $("#pointer").html("<span style='color:" + products[names[this.INTERSECTED].n].color + "'>" +
                    countries[names[this.INTERSECTED].c].name + "出口" + products[names[this.INTERSECTED].n].name + ' $' +
                    products[names[this.INTERSECTED].n].sales + "</span>");
                highLightCountry(countries[names[this.INTERSECTED].c], true);
            } else {
                $("#pointer").css({top: -100, left: 0});
                UserInterface.changeCursor("default");
                selectedID = null;
                highLightCountry(null, false);
            }
        }

    }

    //鼠标指到这个国家里面的时候调用的方法，将当前高亮的国家转回普通，然后将当前国家的边界高亮
    function highLightCountry(country, on) {
        //如果当前已经有别的国家被高亮了，那么将这个国家先给变为普通状态
        if (countryOverlay) {
            scene.remove(countryOverlay);
            countryOverlay = new THREE.Object3D();
        }
        if (on) {
            meshes = country.polygons;
            if (!countryOverlay) countryOverlay = new THREE.Object3D();
            if (meshes != null)
                for (var i = 0; i < meshes.length; i++) {
                    currentMesh = shape.children[0].getObjectById(meshes[i], true).geometry.vertices;
                    geoMeshline = new GeoMeshLine(currentMesh, {
                        resolution: [window.innerWidth, window.innerHeight],
                        color: 0xFFFFFF,
                        lineWidth: 2,
                    });
                    countryOverlay.add(geoMeshline);
                }
            scene.add(countryOverlay);
        }
    }

    /*鼠标按下的反应
    * 在非story模式的时候，在产品空间中，即转移到该点；
    * 在地图模式中，则相当于选中那个点
    * 如果在没有点的地方点击，那么释放当前选中的点*/
    function mouseDown(e) {
        mouseCoord.x = e.clientX || e.pageX;
        mouseCoord.y = e.clientY || e.pageY;
        isClicking = true;
        if (names[selectedID]) {
            var co = names[selectedID].c;
            $(".countrySelection").select2("val", co);

        } else {
            chosenCountry = null;
            UserInterface.changeCursor("grab", cameraControls.isLocked());
        }
    }


    //设置目标国家
    function targetCountry(co, linksOn, center) {
        parseURL.update_url(currentSetup, selectedCountry);//更新url
        filterCountry = co;
        var target = countries[co];
        if (target) {
            if (linksOn)
                addLinks("countries2D", co);
            cameraControls.center(target.lat * 1.55, target.lon * 1.55, 0);
        }
    }

    //每次滚轮的转动改变zoom 0.005
    function mousewheel(event) {
        var fov;
        if (event.wheelDeltaY)
            fov = event.wheelDeltaY * 0.005;
        else fov = -event.detail / 10;
        cameraControls.zoom(fov);
    }

    //？？？？隐藏没有被选择的category的product点
    function hideCategories() {
        var v = 0;
        var randomCity, country = null;
        var colors = {};
        var count = 0;
        var xaxis = 0;
        yaxis = 0, total = 0;
        loaded = false;
        var indexer = {};
        for (var i = 0; i < countryIndex; i++) {
            $.each(countries, function (p, o) {
                if (i == o.id) {
                    country = o;
                    code = p;
                }
            });
            if (country) {
                for (var product in country["products"]) {
                    cat = categories[products[product].color];
                    if (!indexer[products[product].color]) {
                        indexer[products[product].color] = total;
                        total += cat["total"];
                    }
                    xaxis = cat.id;
                    for (var s = 0; s < Math.round(country["products"][product] / dollars); s++) {
                        index = cat["total"];
                        if (!cat.active) {

                            destination[v * 3 + 0] = (indexer[products[product].color] + Math.random() * cat["total"]) / particles * window.innerWidth / 4 - window.innerWidth / 8;
                            destination[v * 3 + 1] = Math.random() * 5 - window.innerHeight;
                            destination[v * 3 + 2] = 0;

                        }
                        v++;
                    }
                }
            }
        }
        loaded = true;
    }

    //switch 想要到达的状态然后计算并展示
    function switcher(to, reset, incremental) {
        increment = incremental;//增量
        if (currentSetup !== to || reset) {
            if (!reset) {
                //如果当前状态不是to并且没有reset那么：
                cameraControls.reset();
                cameraControls.lockRotation(false);
                particleSystem.rotation.set(0, 0, 0);
                if (darkMode)
                    scene.fog = new THREE.FogExp2(0x000000, 0.0001);
                else
                    scene.fog = new THREE.FogExp2(0x00ffff, 0.0001);

                cameraControls.center(0, 0, 0);
                cameraSpeed = 5;
                shape.position.set(0, 0, 0);
            }

            var v = 0;
            scene.remove(shape);

            Labels.resetLabels(countries, darkMode);
            zoomlock = false;
            scene.remove(links);

            $(".selectionBox").stop().fadeIn();//停止正在运行的动画并渐进出现

            //普通的2D均匀展示

            cameraControls.lockRotation(true);
            previousMode = "2D";
            scene.add(shape);
            var v = 0;
            loaded = false;
            zoomlock = true;
            cameraControls.center(-40, 0, 10);
            var randomCity, country = null;
            var colors = {};
            var count = 0;
            var xaxis = 0;
            yaxis = 0;

            function shapeCentroid(poly) {
                var totalx = 0, totaly = 0, totalz = 0, perimeter = 0;
                for (var l = 0; l < poly.length; l++) {
                    totalx += poly[l].x;
                    totaly += poly[l].y;
                    totalz += poly[l].z;
                    if (l < poly.length - 1) {
                        perimeter += Math.sqrt(Math.pow(poly[l].x - poly[l + 1].x, 2) + Math.pow(poly[l].y - poly[l + 1].y, 2) + Math.pow(poly[l].z - poly[l + 1].z, 2));
                    }
                }
                return [totalx / poly.length * 0.7, totaly / poly.length * 0.7, totalz / poly.length * 0.7, perimeter];
            }

            for (var i = 0; i < countryIndex; i++) {
                $.each(countries, function (p, o) {
                    if (i == o.id) {
                        country = o;
                        code = p;
                    }
                });
                IDs = country.polygons;
                var dotspacing = Math.pow(country.particles / country.area, 0.5) * 40;
                if (IDs) {
                    var p = 0;
                    while (p < country.particles) {
                        for (var k = 0; k < IDs.length; k++) {
                            countryline = shape.children[0].getObjectById(IDs[k]);

                            test = shapeCentroid(countryline.geometry.vertices);

                            for (var j = 0; j < countryline.geometry.vertices.length - 1; j++) {

                                r = Math.floor(Math.random() * (countryline.geometry.vertices.length - 1));
                                vector = countryline.geometry.vertices[r];
                                vector2 = countryline.geometry.vertices[r + 1];
                                for (var u = 0; u < Math.sqrt(Math.pow(vector.x - vector2.x, 2) + Math.pow(vector.y - vector2.y, 2) + Math.pow(vector.z - vector2.z, 2)) / test[3] * countryline.geometry.vertices.length; u++) {
                                    rand = Math.random();

                                    newx = -(vector.x + rand * (vector2.x - vector.x)) * 0.7;
                                    newy = (vector.z + rand * (vector2.z - vector.z)) * 0.7;
                                    newz = (vector.y + rand * (vector2.y - vector.y)) * 0.7;
                                    theta = (90 - country.lon) * Math.PI / 180;
                                    phi = (country.lat) * Math.PI / 180 + Math.PI / 2;
                                    //rand=0.5+(Math.random()-0.5)*Math.random();
                                    //rand=0.25+(Math.random()-0.25)*Math.random();
                                    rand = Math.random();
                                    //rand= Math.round(rand*dotspacing*30)/dotspacing/30;
                                    //rand = 1-Math.random() * Math.random(); //powder
                                    /*ray = globeSize + (1 - rand) * Math.PI * 2;
                                    newx2 = (ray * Math.sin(theta) * Math.cos(phi));
                                    newy2 = (ray * Math.sin(theta) * Math.sin(phi));
                                    newz2 = (ray * Math.cos(theta));*/
                                    offsetX = 0, offsetY = 0, offsetZ = 0;
                                    if (k == 1 && code == "CN") offsetZ = 10;
                                    if (k === 9 && code == "RU") offsetZ = 50;
                                    if (k === 0 && code == "IN") offsetY = -15;
                                    if (k === 0 && code == "AE") offsetZ = 3;
                                    if (k === 0 && code == "BR") offsetX = 20;
                                    if (k === 1 && code == "GB") offsetX = 2;
                                    if (k === 5 && code == "US") offsetY = 14;
                                    if (k === 1 && code == "JP") offsetX = -3;
                                    if (k === 10 && code == "CA") offsetZ = 20;
                                    if (k === 2 && code == "IT") {
                                        if (r < 10 || r > 38) offsetZ = -5;
                                        offsetX = offsetZ;
                                    }
                                    newx2 = -test[0] + (2 * Math.random() - 1) * rand - offsetX;
                                    newy2 = test[2] + (2 * Math.random() - 1) * rand - offsetY;
                                    newz2 = test[1] + (2 * Math.random() - 1) * rand - offsetZ;
                                    //len=Math.sqrt(Math.pow(vector.x-newx2,2)+Math.pow(vector.y-newy2,2)+Math.pow(vector.z-newz2,2));

                                    //mod=1+country.area/150000000;
                                    mod = 1;
                                    newx2 = newx2 * (mod);
                                    newy2 = newy2 * (mod);
                                    newz2 = newz2 * (mod);

                                    if (p < country.particles) {
                                        newpoint = {
                                            "x": newx + rand * (newx2 - newx),
                                            "y": newy + rand * (newy2 - newy),
                                            "z": newz + rand * (newz2 - newz)
                                        };
                                        newpoint2 = {"x": test[0], "y": test[2], "z": test[1]};
                                        //if(code=="IT" ||code=="MX"||code=="JP"||code=="VN"||code=="TH"||code=="GB")polytest=!outofPoly(vector,vector2,newpoint);
                                        polytest = false;
                                        if (polytest) {
                                            destination[v * 3 + 0] = 0;
                                            destination[v * 3 + 1] = 0;
                                            destination[v * 3 + 2] = 0;
                                        } else {
                                            destination[v * 3 + 0] = -Math.round(newpoint.x * dotspacing) / dotspacing;
                                            destination[v * 3 + 2] = -Math.round(newpoint.y * dotspacing) / dotspacing;
                                            destination[v * 3 + 1] = Math.round(newpoint.z * dotspacing) / dotspacing;
                                        }
                                        v++;
                                        p++;
                                    } else {
                                        break;
                                    }

                                }
                            }
                        }
                    }
                } else {
                    for (var r = 0; r < country.particles; r++) {
                        destination[v * 3 + 0] = 0;
                        destination[v * 3 + 1] = 0;
                        destination[v * 3 + 2] = 0;
                        v++;
                    }
                }
            }
            loaded = true;

        }
        particlesPlaced = 0;
        currentSetup = to;
        $("#countrySection").show();
        $("#productSection").hide();

        hideCategories();
    }

    $("#backgroundButton").click(function () {
        darkMode = !darkMode;
    });


    //点击category选择product类别的时候所调用的方法
    $("#categories").on("click", ".chooseCategory", function () {
        var id = $(this).prop("id");
        id = id.substring(3, id.length);
        IDcode = parseInt(id);
        var reset = false;
        $.each(categories, function (a, b) {
            if (IDcode === b.id) {
                if (b.active) reset = true;
                b.active = true;
            } else {
                if (b.active) reset = false;
                b.active = false;
            }
        });
        $.each(categories, function (a, b) {
            if (reset) {
                b.active = true;
                $("#cat" + b.id).removeClass("categorySelected");
            } else {
                if (b.active) {
                    $("#cat" + b.id).addClass("categorySelected");
                }
                else {
                    $("#cat" + b.id).removeClass("categorySelected");
                }
            }
        });
        switcher(currentSetup, true, 5);
    });

    //选择国家
    $("#countries").on('click', '.chosenCountry', function () {
        $(".countrySelection").select2("val", $(this).prop('id'));
    });

    $("#countries").on('mouseout', '.chosenCountry', function () {
        hoverHTML = $(this).html();
        $(this).html(hoverHTML.substring(0, hoverHTML.length - 8));
    });

    $("#countries").on('mouseover', '.chosenCountry', function () {
        hoverHTML = $(this).html();
        hoverHTML += "(点击查看连线)";
        $(this).html(hoverHTML);

        selectedCountry = $(this).prop("id");
        highLightCountry(countries[selectedCountry], true);

        $("#pointer").css({top: -100, left: 0});
    });


    function existstory() {
        $("#storyPrompt").stop().fadeOut();
        cameraControls.loaded();
        $("#UI").fadeIn();
    }

    //高亮与正常模式之间的切换
    $("#contrastbutton").click(function () {
        if (!contrast) {
            $(this).html("正常");
            contrast = true;
            constantSize = true;
            changePointSize(3);
            lines = shape.children[0];
            for (var i = 0; i < lines.children.length; i++) {
                lines.children[i].material.linewidth = 6
            }
        } else {
            $(this).html("高亮");
            contrast = false;
            constantSize = false;

            lines = shape.children[0];
            for (var i = 0; i < lines.children.length; i++) {
                lines.children[i].material.linewidth = 2
            }
            animatePointSize(true);
        }
    });

    //根据当前的比例尺设定point的大小
    function animatePointSize(reset) {
        testZoom = Math.round(Math.log(431 - particleSystem.position.z));
        levels = [0.23, 0.23, 0.4, 0.8, 1, 1.3, 1.35, 1.38, 1.4, 1.41, 1.413, 1.4];
        if (testZoom !== currentZoom || reset) {
            currentZoom = testZoom;
            var sizes = geometry.attributes.size.array;
            for (var v = 0; v < particles / percentage; v++) {
                sizes[v] = levels[currentZoom];
            }
            geometry.attributes.size.needsUpdate = true;
        }

    }

    //改变点的大小，在产品空间的时候不起作用
    function changePointSize(size) {
        var sizes = geometry.attributes.size.array;
        for (var v = 0; v < particles / percentage; v++) {
            sizes[v] = size;
        }
        geometry.attributes.size.needsUpdate = true;
    }

    function animateOverlay(percentage) {
        //对于第一二种模式
        var test = true;
        //测试目录中每个类型的活跃度
        $.each(categories, function (col, val) {
            if (!val.active) test = false;
        });
        if (test) {
            //如果所有点都安放好的话，边界就改变透明度
            if (percentage === 0) {//如果还有没安放好的点的话
                overlayMaterial.opacity = Math.min(((cameraControls.getZoom() - 175) / 300), 0.6);
            } else {
                overlayMaterial.opacity = Math.min(percentage / 100, 0.6);
            }
        } else {
            overlayMaterial.opacity = 0;
        }
    }

    //动画
    function animate() {
        //如果Labels非空，那么就对不同模式展示不同的Label
        if (Labels)
            Labels.animateLabels(countries, geometry, currentSetup, particleSystem);

        if (loaded) {
            if (links)
                links.position.set(particleSystem.position.x, particleSystem.position.y, particleSystem.position.z);
            animateLinks();

            var positions = geometry.attributes.position.array;
            var currentColor = new THREE.Color();
            error = 0.2;
            var a = false, b = false, c = false, fin = true;
            //不停地改变点的位置直到它的位置达到目标位置
            if (increment > 0) {
                for (var v = 0; v < particles / percentage; v++) {
                    a = false, b = false, c = false;
                    //easing=Math.sin((0.55+(v%100)/100*0.4)*Math.PI);
                    easing = 0.2 + (v % 1000) / 1000;
                    if (Math.abs(positions[v * 3 + 0] - destination[v * 3 + 0]) > error)
                        positions[v * 3 + 0] += (destination[v * 3 + 0] - positions[v * 3 + 0]) / increment * easing;
                    else {
                        positions[v * 3 + 0] = destination[v * 3 + 0];
                        a = true;
                    }
                    if (Math.abs(positions[v * 3 + 1] - destination[v * 3 + 1]) > error)
                        positions[v * 3 + 1] += (destination[v * 3 + 1] - positions[v * 3 + 1]) / increment * easing;
                    else {
                        positions[v * 3 + 1] = destination[v * 3 + 1];
                        b = true;
                    }
                    if (Math.abs(positions[v * 3 + 2] - destination[v * 3 + 2]) > error)
                        positions[v * 3 + 2] += (destination[v * 3 + 2] - positions[v * 3 + 2]) / increment * easing;
                    else {
                        positions[v * 3 + 2] = destination[v * 3 + 2];
                        c = true;
                    }
                    if (a && b && c) {
                        particlesPlaced++;
                    } else {
                        fin = false;
                    }
                }

                if (fin) {
                    increment = 0;
                    for (var v = 0; v < particles; v++) {
                        positions[v * 3 + 0] = destination[v * 3 + 0];
                        positions[v * 3 + 1] = destination[v * 3 + 1];
                        positions[v * 3 + 2] = destination[v * 3 + 2];
                    }
                }
                animateOverlay(particlesPlaced / particles);
            } else {
                animateOverlay(0);
            }
            geometry.attributes.position.needsUpdate = true;
            animatePointSize(false);
        }
        cameraControls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    }
};