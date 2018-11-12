if (WebGLtest()) {
        init();
        animate();
    } else {
        $("#storyPrompt").html($("#noWebGL").html());
    }