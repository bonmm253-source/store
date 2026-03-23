const toggleBtn = document.getElementById('togglebtn');
const sideBar = document.getElementById('sidebar');
const darkToggle =  document.getElementById('darkmodeToggle');
const modeIcon = document.getElementById('modeicon');

toggleBtn.addEventListener("click",() => {
sideBar.classList.toggle("collapsed");
} );

darkToggle.addEventListener("change", () => {
    document.body.classList.toggle("dark");
    if(document.body.classList.contains("dark")){
        modeIcon.classList.replace("bx-sun", "bx-moon")
    } else{
        modeIcon.classList.replace("bx-moon", "bx-sun");
    }
})


