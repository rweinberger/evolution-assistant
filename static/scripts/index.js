$(window).on('load', function() {
    let formNum = 1;
    const scoButton = $("#add-sco");
    const scoForm = $("#sco-forms");

    function delSco() {
        $(this).parent().remove();
    }

    const addScoForm = (e) => {
        e.preventDefault();
        formNum++;

        // clone old form
        const newForm = $("#og-form").clone(true, true);

        // update attributes on clones
        newForm.removeAttr("id");
        newForm.children().each(function() {
            const oldName = this.name;
            const newName = oldName.slice(0, -1) + String(formNum);
            $(this).attr("name", newName);
        })

        // add delete button for all subsequent entries
        const delBtn = $("<button class='del-btn'>x</button>");
        delBtn.on("click", delSco);

        newForm.append(delBtn);
        scoForm.append(newForm);
    }

    scoButton.on("click", addScoForm);
})