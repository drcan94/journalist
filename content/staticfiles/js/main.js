window.setTimeout(function () {
    $(".alert.timer").fadeTo(500, 0).slideUp(500, function () {
        $(this).remove();
    });

}, 1000 * 2.5);

let prevScrollpos = window.pageYOffset;
window.onscroll = function () {
    let currentScrollPos = window.pageYOffset;
    if (prevScrollpos > currentScrollPos) {
        document.getElementById("top-nav").style.top = "0";
    } else {
        document.getElementById("top-nav").style.top = "-60px";
    }
    prevScrollpos = currentScrollPos;
}


$(document).ready(function () {

    document.onclick = function (e) {

        if (e.target.id !== "items-logo" && e.target.id !== "left-column" && e.target.id !== "toggle" && !$(e.target).parents().hasClass('items-left') && !$(e.target).hasClass('items-left')) {
            $("#left-column").removeClass("active");
            $("#toggle").removeClass("active");
            $(".items-left").removeClass("active");
            if (window.innerWidth < 400) {
                $("#right-column").removeClass("active").css("filter", "none").css("-webkit-filter", "none");
            } else {
                $("#right-column").removeClass("active")
            }
            $("#top-nav").removeClass("active").css("width", "100%");
            $("#items-logo").css("display", "none");
        }

        if (e.target.id === "toggle" && !$(e.target).hasClass('active')) {
            $("#items-logo").css("display", "none");
            $("#top-nav").removeClass("active").css("width", "100%");

            if (window.innerWidth < 400) {
                $("#right-column").removeClass("active").css("filter", "none").css("-webkit-filter", "none");
            } else {
                $("#right-column").removeClass("active")
            }
        }

    }

    $("#toggle").click(function () {
        $(this).siblings().removeClass("active");
        $(this).toggleClass("active");
        $("#left-column").toggleClass("active");
        if (window.innerWidth < 400) {
            $("#right-column").toggleClass("active").css("filter", "blur(8px)").css("-webkit-filter", "blur(8px)");
            $("#top-nav").toggleClass("active").css("width", "100%");
        } else {
            $("#right-column").toggleClass("active")
            $("#top-nav").toggleClass("active").css("width", "calc(100% - 100px)");
        }

        $("#items-logo").css("display", "flex")


    })

});


function highlightCurrent() {
    const curPage = document.URL;
    const links = document.getElementsByTagName('a');
    for (let link of links) {
        if (link.href === curPage) {
            link.classList.add("currentLink");
        }
    }
}

document.onreadystatechange = () => {
    if (document.readyState === 'complete') {
        highlightCurrent()
    }
};


let getSiblings = function (x) {
    var siblings = [];
    var sibling = x.parentNode.firstChild;

    while (sibling) {
        if (sibling.nodeType === 1 && sibling !== x) {
            siblings.push(sibling);
        }
        sibling = sibling.nextSibling
    }

    return siblings;

};

const sub_menu = document.querySelectorAll(".sub-menu");
sub_menu.forEach(function (i) {
    i.parentElement.addEventListener("click", function (e) {
        getSiblings(i.parentElement).forEach(function (j) {
            j.classList.remove("active")
        })
        i.parentElement.classList.toggle("active")

        if (innerHeight < 260) {
            if (i.clientHeight < innerHeight) {
                if (e.clientY < i.clientHeight / 2) {
                    i.style = "";
                    i.style.top = "0";
                } else if (innerHeight - i.clientHeight / 2 > e.clientY) {
                    i.style = "";
                    i.style.top = e.clientY + "px";
                    i.style.transform = "translateY(-50%)";

                } else {
                    i.style = "";
                    i.style.bottom = "0";
                }
                i.style.maxHeight = innerHeight + "px";

            } else {
                i.style = "";
                i.style.maxHeight = innerHeight + "px";
                i.style.top = "0";
            }


        } else {
            if (e.clientY < 130) {
                i.style = "";
                i.style.top = "0";
            } else if (innerHeight - 130 > e.clientY) {
                i.style = "";
                i.style.top = e.clientY + "px";
                i.style.transform = "translateY(-50%)";

            } else {
                i.style = "";
                i.style.bottom = "0";
            }
            i.style.maxHeight = "260px";
        }


    })

})


