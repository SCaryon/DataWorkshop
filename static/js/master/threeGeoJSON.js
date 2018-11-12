/* Draw GeoJSON

Iterates through the latitude and longitude values, converts the values to XYZ coordinates, 
and draws the geoJSON geometries.

*/

var x_values = [];
var y_values = [];
var z_values = [];
var lines = new THREE.Object3D();
var segments = new THREE.Geometry();

function drawThreeGeo(json, radius, shape, options) {

    var json_geom = createGeometryArray(json);
    //An array to hold the feature geometries.
    var convertCoordinates = getConversionFunctionName(shape);
    //Whether you want to convert to spherical or planar coordinates.
    var coordinate_array = [];
    //Re-usable array to hold coordinate values. This is necessary so that you can add 
    //interpolated coordinates. Otherwise, lines go through the sphere instead of wrapping around.

    for (var geom_num = 0; geom_num < json_geom.length; geom_num++) {

        if (json_geom[geom_num].type == 'Point') {
            convertCoordinates(json_geom[geom_num].coordinates, radius);
            drawParticle(y_values[0], z_values[0], x_values[0], options);

        } else if (json_geom[geom_num].type == 'MultiPoint') {
            for (var point_num = 0; point_num < json_geom[geom_num].coordinates.length; point_num++) {
                convertCoordinates(json_geom[geom_num].coordinates[point_num], radius);
                drawParticle(y_values[0], z_values[0], x_values[0], options);
            }

        } else if (json_geom[geom_num].type == 'LineString') {
            coordinate_array = createCoordinateArray(json_geom[geom_num].coordinates);

            for (var point_num = 0; point_num < coordinate_array.length; point_num++) {
                convertCoordinates(coordinate_array[point_num], radius);
            }
            drawLine(y_values, z_values, x_values, options);

        } else if (json_geom[geom_num].type == 'Polygon') {
            for (var segment_num = 0; segment_num < json_geom[geom_num].coordinates.length; segment_num++) {
                coordinate_array = createCoordinateArray(json_geom[geom_num].coordinates[segment_num]);

                for (var point_num = 0; point_num < coordinate_array.length; point_num++) {
                    convertCoordinates(coordinate_array[point_num], radius);
                }
                drawLine(y_values, z_values, x_values, options);
            }

        } else if (json_geom[geom_num].type == 'MultiLineString') {
            for (var segment_num = 0; segment_num < json_geom[geom_num].coordinates.length; segment_num++) {
                coordinate_array = createCoordinateArray(json_geom[geom_num].coordinates[segment_num]);

                for (var point_num = 0; point_num < coordinate_array.length; point_num++) {
                    convertCoordinates(coordinate_array[point_num], radius);
                }
                drawLine(y_values, z_values, x_values, options);
            }

        } else if (json_geom[geom_num].type == 'MultiPolygon') {
            for (var polygon_num = 0; polygon_num < json_geom[geom_num].coordinates.length; polygon_num++) {
                for (var segment_num = 0; segment_num < json_geom[geom_num].coordinates[polygon_num].length; segment_num++) {
                    coordinate_array = createCoordinateArray(json_geom[geom_num].coordinates[polygon_num][segment_num]);

                    for (var point_num = 0; point_num < coordinate_array.length; point_num++) {
                        convertCoordinates(coordinate_array[point_num], radius);
                    }
                    drawLine(y_values, z_values, x_values, options);
                }
            }
        } else {
            throw new Error('The geoJSON is not valid.');
        }
    }

    lines.position.set(700, -300, 0);
    scene.add(lines);
    return lines;
}

function createGeometryArray(json) {
    var geometry_array = [];

    if (json.type == 'Feature') {
        geometry_array.push(json.geometry);
    } else if (json.type == 'FeatureCollection') {
        for (var feature_num = 0; feature_num < json.features.length; feature_num++) {
            geometry_array.push(json.features[feature_num].geometry);
        }
    } else if (json.type == 'GeometryCollection') {
        for (var geom_num = 0; geom_num < json.geometries.length; geom_num++) {
            geometry_array.push(json.geometries[geom_num]);
        }
    } else {
        throw new Error('The geoJSON is not valid.');
    }
    //alert(geometry_array.length);
    return geometry_array;
}

function getConversionFunctionName(shape) {
    var conversionFunctionName;

    if (shape == 'sphere') {
        conversionFunctionName = convertToSphereCoords;
    } else if (shape == 'plane') {
        conversionFunctionName = convertToPlaneCoords;
    } else {
        throw new Error('The shape that you specified is not valid.');
    }
    return conversionFunctionName;
}

//将原有的feature中连续性较低的一些点中间填上一些点使边界更为连续
function createCoordinateArray(feature) {
    //Loop through the coordinates and figure out if the points need interpolation.
    var temp_array = [];
    var interpolation_array = [];

    for (var point_num = 0; point_num < feature.length; point_num++) {
        var point1 = feature[point_num];
        var point2 = feature[point_num - 1];

        if (point_num > 0) {
            if (needsInterpolation(point2, point1)) {
                interpolation_array = [point2, point1];
                interpolation_array = interpolatePoints(interpolation_array);

                for (var inter_point_num = 0; inter_point_num < interpolation_array.length; inter_point_num++) {
                    temp_array.push(interpolation_array[inter_point_num]);
                }
            } else {
                temp_array.push(point1);
            }
        } else {
            temp_array.push(point1);
        }
    }
    return temp_array;
}

//如果两个点的横纵坐标距离有一个大于5，那么返回true，说明他们需要中间节点
function needsInterpolation(point2, point1) {
    //If the distance between two latitude and longitude values is 
    //greater than five degrees, return true.
    var lon1 = point1[0];
    var lat1 = point1[1];
    var lon2 = point2[0];
    var lat2 = point2[1];
    var lon_distance = Math.abs(lon1 - lon2);
    var lat_distance = Math.abs(lat1 - lat2);

    if (lon_distance > 5 || lat_distance > 5) {
        return true;
    } else {
        return false;
    }
}

//一直给两个点增加中间节点直到不需要为止，返回所有的中间节点的坐标
function interpolatePoints(interpolation_array) {
    //This function is recursive. It will continue to add midpoints to the 
    //interpolation array until needsInterpolation() returns false.
    var temp_array = [];
    var point1, point2;

    for (var point_num = 0; point_num < interpolation_array.length - 1; point_num++) {
        point1 = interpolation_array[point_num];
        point2 = interpolation_array[point_num + 1];

        if (needsInterpolation(point2, point1)) {
            temp_array.push(point1);
            temp_array.push(getMidpoint(point1, point2));
        } else {
            temp_array.push(point1);
        }
    }

    temp_array.push(interpolation_array[interpolation_array.length - 1]);

    if (temp_array.length > interpolation_array.length) {
        temp_array = interpolatePoints(temp_array);
    } else {
        return temp_array;
    }
    return temp_array;
}

//获取两个节点的中间节点
function getMidpoint(point1, point2) {
    var midpoint_lon = (point1[0] + point2[0]) / 2;
    var midpoint_lat = (point1[1] + point2[1]) / 2;
    var midpoint = [midpoint_lon, midpoint_lat];

    return midpoint;
}

//将坐标转换成球状坐标
function convertToSphereCoords(coordinates_array, sphere_radius) {
    var lon = coordinates_array[0];
    var lat = coordinates_array[1];

    x_values.push(Math.cos(lat * Math.PI / 180) * Math.cos(lon * Math.PI / 180) * sphere_radius);
    y_values.push(Math.cos(lat * Math.PI / 180) * Math.sin(lon * Math.PI / 180) * sphere_radius);
    z_values.push(Math.sin(lat * Math.PI / 180) * sphere_radius);
}

//将坐标转换成平面坐标
function convertToPlaneCoords(coordinates_array, radius) {
    var lon = coordinates_array[0];
    var lat = coordinates_array[1];

    z_values.push((lat / 180) * radius);
    y_values.push((lon / 180) * radius);
}

//画一个点
function drawParticle(x, y, z, options) {
    var particle_geom = new THREE.Geometry();
    particle_geom.vertices.push(new THREE.Vector3(x, y, z));
    var particle_material = new THREE.ParticleSystemMaterial(options);
    var particle = new THREE.ParticleSystem(particle_geom, particle_material);
    scene.add(particle);

    clearArrays();
}

//给出坐标点集，组成一条线，将折线放入lines里面
function drawLine(x_values, y_values, z_values, options) {
    var line_geom = new THREE.Geometry();
    createVertexForEachPoint(line_geom, x_values, y_values, z_values);

    var line_material = new THREE.LineBasicMaterial(options);
    var line = new THREE.Line(line_geom, line_material);
    if (x_values[0] > -1000 && x_values[0] < -300 && y_values[0] > 150)
        lines.add(line);
    clearArrays();
}


//将x，y，z坐标放入全局的segments里面，并放入object_geometry中
function createVertexForEachPoint(object_geometry, values_axis1, values_axis2, values_axis3) {
    for (var i = 0; i < values_axis1.length; i++) {
        object_geometry.vertices.push(new THREE.Vector3(values_axis1[i],
            values_axis2[i], values_axis3[i]));
        segments.vertices.push(new THREE.Vector3(values_axis1[i], values_axis2[i], values_axis3[i]));
    }
}

//清空x,y,z
function clearArrays() {
    x_values.length = 0;
    y_values.length = 0;
    z_values.length = 0;
}