let formNum = 1;

$(window).on('load', function() {
    const scoButton = $("#add-sco");
    const scoForm = $("#sco-forms");

    function delSco() {
        $(this).parent().remove();
    }

    // make sure original form has listeners
    addFormListener('target1');

    const addScoForm = (e) => {
        e.preventDefault();
        formNum++;

        // clone old form
        const newForm = $("#og-form").clone(true, true);

        // update attributes on clones
        var classname = updateAttributes(newForm);

        // add delete button for all subsequent entries
        const delBtn = $("<button class='del-btn'>x</button>");
        delBtn.on("click", delSco);

        newForm.prepend(delBtn);
        scoForm.append(newForm);

        // add listener to classname
        addFormListener(classname);
    }

    scoButton.on("click", addScoForm);
})

function updateAttributes(form) {
    form.removeAttr("id");
    form.children().each(function() {
        const oldClass = this.className;
        const oldClassTarget = 'target1';
        const newClassTarget = 'target' + String(formNum);
        const newClass = oldClass.replace(oldClassTarget, newClassTarget);
        $(this).removeClass(oldClass).addClass(newClass);

        const oldName = this.name;
        if (oldName != null) {
            const newName = oldName.slice(0, -1) + String(formNum);
            $(this).attr("name", newName);
        }
    })
    return 'target' + String(formNum);
}

function showForm(classname, sco) {
    const targetClass = $('.' + classname + '-ext');
    switch (sco) {
        case "ADD_COLUMN":
        case "DROP_COLUMN":
        case "RENAME_COLUMN":
        case "ADD_TABLE":
        case "DROP_TABLE":
        case "RENAME_TABLE":
    }
    if (targetClass.css('display') == 'none') {
        targetClass.css("display", "block");
    }
}

function detectFormSelection(classname) {
    return function() {
        allSelected = true;
        let sco = null;
        $('.' + classname).each(function() {
            if ($(this).val() === '' || $(this).val() === null) {
                allSelected = false;
                return;
            }

            if ($(this).hasClass("sco-select")) sco = $(this).val();
        })
        if (allSelected) showForm(classname, sco);
    }
}

function addFormListener(classname) {
    $('.' + classname).each(function() {
        $(this).change(detectFormSelection(classname));
    })
}