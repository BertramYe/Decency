import * as THREE from 'three'
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OrbitControls } from "three/addons/controls/OrbitControls.js"
import { STLExporter } from 'three/addons/exporters/STLExporter.js';
import * as mergeBufferGeometries from 'three/addons/utils/BufferGeometryUtils.js';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js'


var camera, scene, renderer;
var width, height
var finalSTLName = "";
var wordsColorControl;
var brickColorControl;
// input
var inputString = document.getElementById("inputStringChar")
// the container 
width = window.innerWidth * 0.5;
height = window.innerHeight * 0.5;
// the gui
const gui = new GUI();
var gui_right = width * 0.5 + "px"
gui.domElement.style.right = gui_right

var container = document.getElementById('container')
// gui style
var container_width = width + "px";
var container_height = height + "px";
// container
container.style.width = container_width
container.style.height = container_height




// click the gen stl
var genstlButton = document.getElementById("genSTL")
genstlButton.addEventListener('click', genSTLClick)
function genSTLClick() {
    var inputStr = inputString.value.trim();
    if (inputStr != "") {
        var stlStrPathList = GetStlPath(inputStr)
        init(stlStrPathList);
        animate();
        finalSTLName = inputStr
    } else {
        alert("the input content should not be the empty! please re-input the right char");
        // containerHasRender = false;
    }

}


// download stl files
var downloadSTLButton = document.getElementById("download")
downloadSTLButton.addEventListener('click', downloadSTLFile)
function downloadSTLFile() {
    if (scene && finalSTLName != "") {
        var downloaded = exportSTL(scene, finalSTLName)
        if (!downloaded) {
            alert("download failed!")
        }

    } else {
        alert("download failed!")
    }

}



// init to gen the words
function init(stlStrPathList) {
    var container = document.getElementById('container');

    // create a scene
    scene = new THREE.Scene();
    scene.add(new THREE.HemisphereLight());

    // create a camera
    camera = new THREE.PerspectiveCamera(90, width / height, 0.1, 500);
    camera.position.set(0, -20, 0)
    camera.lookAt(0, 0, 0)


    // create a light 
    // var ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    // scene.add(ambientLight);
    // gui.add(ambientLight, 'intensity', 0, 1)

    // the direct light
    // 3) 平行光，很简单就不过多介绍了
    // 设置平行光需要更多一步指定平行光照射的方向的参考对象，因为两点之间确定一条直线
    const directionalLighter = new THREE.DirectionalLight(0Xffffff, 1.0)
    // 这里代表平行光直接照射向mesh本身，如果不指定，就是指定target就是指向原点(0,0,0)
    // directionalLighter.target = mesh 
    // 如果不指定平行光的位置，默认他就从Y轴，从上往下照射
    directionalLighter.position.set(0, -50, 20)
    // directionalLighter.position.set(20, 30, -5);

    // tuen on the shadow
    directionalLighter.castShadow = true;
    // the shadow scope
    directionalLighter.shadow.mapSize.width = 1024; // 设置阴影贴图的宽度
    directionalLighter.shadow.mapSize.height = 1024; // 设置阴影贴图的高度
    directionalLighter.shadow.bias = -0.5; // 设置阴影的偏移量
    directionalLighter.shadow.camera.near = 1; // 设置阴影相机的近裁剪面距离
    directionalLighter.shadow.camera.far = 100; // 设置阴影相机的远裁剪面距离
    directionalLighter.shadow.camera.fov = 45; // 设置阴影相机的视角


    // 将平行光添加到场景里面
    scene.add(directionalLighter)
    // gui.add(directionalLighter,'intensity',0,1)

    // loader the STL files
    var loader = new STLLoader();
    LoadSTLFile(stlStrPathList, scene, loader)







    // // 创建一个三维坐标轴
    // // 并指定坐标轴的大小,坐标轴颜色红R、绿G、蓝B分别对应坐标系的x、y、z轴
    // // three.js 中默认y轴朝上
    // const axesHelper = new THREE.AxesHelper(8000);
    // // // 将坐标轴添加到场景中
    // scene.add(axesHelper);

    // const lighterhelper = new THREE.DirectionalLightHelper(directionalLighter, 10)
    // scene.add(lighterhelper);




    renderer = new THREE.WebGLRenderer({
        antialias: true,
        // precision: 'highp',
        alpha: true
    });

    // trun on the shadow
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap

    renderer.setPixelRatio(window.devicePixelRatio); // 设置像素比
    // set the canvars width
    renderer.setSize(width, height);

    // remove the replicate containers'element
    if (container.children.length > 0) {
        container.removeChild(container.children[0])
    }
    container.appendChild(renderer.domElement);
    // set the background color
    container.children[0].style.backgroundColor = "linear-gradient(to bottom, #000000, #676767);";

    // let the the user can turn the 3D mesh
    const controls = new OrbitControls(camera, renderer.domElement);

    // when the page of the 3D has changed , like the mouse moved
    controls.addEventListener("change", function () {
        // console.log('camara.position',camera.position)
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
        // 此处注释掉是因为上面的渲染循环动画在执行时，已经间接的帮助我们OrbitControls控件做了对应的渲染，
        // 这两个功能的结合时，我们不必要多做一次渲染
        // renderer.render(scene, camera); 

    })


    // add the gui to change the words color
    const wordsColorObject = {
        color: 0x00ffff,
    }

    var mergedWordMesh;
    if(!wordsColorControl){
        wordsColorControl = gui.addColor(wordsColorObject, 'color').name('words color')
    }
    wordsColorControl.onChange(function (value) {
        if (!mergedWordMesh) {
            mergedWordMesh = MergeTargetMesh(scene,"words");
            scene.add(mergedWordMesh)
        }
        mergedWordMesh.material.color.set(value)
    });
       
    // add the gui to change the brick color
    const brickColorObject ={
        color:0x00ffff,
    }
    var brickMesh;
    if(!brickColorControl){
        brickColorControl = gui.addColor(brickColorObject,'color').name('brick color')
    }
    brickColorControl.onChange(function(value){
        if(!brickMesh){
            brickMesh = MergeTargetMesh(scene,"brick");
        }
        brickMesh.material.color.set(value)
    })
    

}


// this the is loop , always rendaer the page
function animate() {
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}



// 设置随着页面的改变，整个显示也随着改变
window.onresize = function () {
    width = window.innerWidth * 0.5;
    height = window.innerHeight * 0.5;
    // the container 
    var container_width = width + "px";
    var container_height = height + "px";
    // gui style
    var gui_right = width * 0.5 + "px"
    gui.domElement.style.right = gui_right
    container.style.width = container_width
    container.style.height = container_height

    // 更新canvas画布尺寸
    if (renderer) {
        renderer.setSize(width, height);
        // 设置相机的比例不变
        camera.aspect = width / height
        // 同时需要更新相机本身的投影矩阵
        camera.updateProjectionMatrix();
    }

}


// get stlPath
function GetStlPath(strInput) {

    // the input string 
    // strInput = "HELLO"
    const stlStrPathList = [];
    const getCharCorrectly = true;
    // get target string path 
    if (strInput.length > 0) {

        // fist put the brick into the STL files path
        stlStrPathList.push('static/web3DResource/mattoncino.stl')
        var lower_parttern = new RegExp("[a-z]+");
        var number_parttern = new RegExp("[0-9]+");
        var upper_parttern = new RegExp("[A-Z]+");

        // loop the input char and put the target char path into the stl file path 
        for (var i = 0; i < strInput.length; i++) {

            var temp_path = ""
            var char = strInput.charAt(i)
            if (lower_parttern.test(char) | number_parttern.test(char) | upper_parttern.test(char) | char == " ") {
                if (lower_parttern.test(char)) {
                    temp_path = "static/web3DResource/lower/" + char + ".stl";

                } else if (number_parttern.test(char)) {
                    temp_path = "static/web3DResource/number/" + char + ".stl"
                } else if (upper_parttern.test(char)) {
                    temp_path = "static/web3DResource/upper/" + char + ".stl"
                } else {
                    temp_path = " "
                }

            } else {
                alert("please input the right content,the input string only allow the number(0-9) " +
                    " the lower char(a-z) and the upper char (A-Z), but for the other chars are not allowed! ")
                getCharCorrectly = false;
            }


            if (temp_path.length > 0) {
                // console.log(temp_path)
                stlStrPathList.push(temp_path)
            }
        };
    }
    // console.log("stlStrPathList",stlStrPathList)
    if (!getCharCorrectly) {
        stlStrPathList = []
    }
    return stlStrPathList;
}



function LoadSTLFile(stlStrPathList, scene, loader) {
    var brickgeometry;
    loader.load(stlStrPathList[0], function (brick_geometry) {
        // brick
        var brick_material = new THREE.MeshLambertMaterial({ color: 'white' });//{ color: 0x00ffff }
        brick_geometry.center();
        var brick_mesh = new THREE.Mesh(brick_geometry, brick_material);
        brickgeometry = brick_geometry;
        brick_mesh.scale.setX(1)
        brick_mesh.scale.setY(1)
        brick_mesh.scale.setZ(0.1)
        // open the shadow
        // and the brick recieave the shadow
        brick_mesh.castShadow = true;
        brick_mesh.receiveShadow = true;
        scene.add(brick_mesh);

    });


    var count = 0
    // var char_mesh=[]
    for (var j = 1; j < stlStrPathList.length; j++) {
        // per stl har position
        loader.load(stlStrPathList[j], function (char_geometry) {
            var char_z = brickgeometry.boundingBox.max.z
            var char_material = new THREE.MeshStandardMaterial({ color: 'white' });//{ color: 0x00ffff }
            // char_mesh.rotation.x = -0.5 * Math.PI; //将模型摆正
            char_geometry.center(); //居中显示
            var char_height = char_geometry.boundingBox.max.z - char_geometry.boundingBox.min.z
            var char_z = char_height / 2
            // var char_width = char_geometry.boundingBox.max.x - char_geometry.boundingBox.min.x
            var avrg_char_width = (brickgeometry.boundingBox.max.x - brickgeometry.boundingBox.min.x) / (stlStrPathList.length - 1)
            var start_x = - (brickgeometry.boundingBox.max.x - brickgeometry.boundingBox.min.x) / 2 + (avrg_char_width / 2)
            var Actul_start_x = start_x + avrg_char_width * count
            var char_mesh = new THREE.Mesh(char_geometry, char_material);
            char_mesh.scale.set(0.2, 0.2, 0.2)
            char_mesh.position.setZ(char_z * 0.2 )
            char_mesh.position.setX(Actul_start_x);
            char_mesh.castShadow
            scene.add(char_mesh);
            count++
        });
    }

}


function exportSTL(scene, finalSTLName) {
    // get all of the merged meshed
    var stl_saved = false;
    var mergeMeshes = MergeTargetMesh(scene,"all")
    if(mergeMeshes){
        var exporter = new STLExporter();
        var stlData = exporter.parse(mergeMeshes);
        // 将 STL 数据保存到文件
        var blob = new Blob([stlData], { type: 'text/plain' });
        // 调用 URL.createObjectURL() 方法创建一个包含 Blob 数据的 URL。该 URL 可以被用作资源的临时地址，使得可以在浏览器中访问该 Blob 数据。
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.id = "downloadstl"
        link.href = url;
        link.download = finalSTLName + '.stl';
        link.click();
        document.body.remove(document.getElementById("downloadstl")) // 下载完移除元素
        // window.URL.revokeObjectURL(href); // 释放掉blob对象

        // console.log("userSaveSTLPath:",userSaveSTLPath,"url:",url)
        location.reload();
        stl_saved = true;
    }
    
    return stl_saved;

}


// merge target mesh
function MergeTargetMesh(scene,type) {

    var mesh_geometry_list = []
    var brickmesh;
    var material_list =[]
    // var color_list = []
    scene.traverse(function (object) {
       
        if (object instanceof THREE.Mesh) {
            // transfer the mesh geometry into WorldGeometry
            if (!(object.material instanceof THREE.MeshLambertMaterial) && type ==="words") {
                // var materialcolor = new THREE.Color(object.material.color.r,object.material.color.g,object.material.color.b)
                // var new_material = new THREE.MeshStandardMaterial({
                //     color:materialcolor,
                // })
                // material_list.push(new_material)
                let matrixWorldGeometry = object.geometry.clone().applyMatrix4(object.matrixWorld);
                mesh_geometry_list.push(matrixWorldGeometry);
            }else if(object.material instanceof THREE.MeshLambertMaterial && type === "brick"){
                brickmesh = object
            }else if(type == "all"){
                // tranfer all of the material as the standerd material
                var materialcolor = new THREE.Color(object.material.color.r,object.material.color.g,object.material.color.b)
                var new_material = new THREE.MeshStandardMaterial({
                    color:materialcolor,
                })
                material_list.push(new_material)
                let matrixWorldGeometry = object.geometry.clone().applyMatrix4(object.matrixWorld);
                mesh_geometry_list.push(matrixWorldGeometry)
            }

        }
    });

    // type : brick, just return the brick mesh
    // type : words, just merge the words mesh into a new mesh
    // type : all , just merge all of the mesh, including the mesh and the brick
    if (type==="brick"){
        return brickmesh
    }else if(type==="words"){
        var mergedGeometry = mergeBufferGeometries.mergeBufferGeometries(mesh_geometry_list, true);
        // merge different words into one merge but without set any color or something
        var mergedMesh = new THREE.Mesh(mergedGeometry, new THREE.MeshStandardMaterial());
        return mergedMesh

    }else{
        var mergedGeometry = mergeBufferGeometries.mergeBufferGeometries(mesh_geometry_list, true);
        // mutiple materials can merged into one with the diferent materils and colos like below
        // var mergedMesh = new THREE.Mesh(mergedGeometry, new THREE.MeshStandardMaterial());
        var mergedMesh = new THREE.Mesh(mergedGeometry, material_list);
        // console.log("mergedMesh",mergedMesh)
        return mergedMesh
    }
    
}

