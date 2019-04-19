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
        const newForm = $("#og-form").clone(false, false);

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
        const newClassTarget = 'target' + String(formNum);
        const newClass = oldClass.replace('target1', newClassTarget);
        $(this).removeClass(oldClass).addClass(newClass);

        const oldName = this.name;
        if (oldName != null) {
            const newName = oldName.replace('1', String(formNum));
            $(this).attr("name", newName);
        }

        if (newClass.includes("-ext")) $(this).empty();
    })
    return 'target' + String(formNum);
}

function addTextBox(target, text, targetNum) {
    const name = 'text#' + targetNum;
    const textBox = $("<input type='text' placeholder='" + text + "' name='" + name + "' required>");
    target.append(textBox);
}

function addColumnSelect(target, table, text, targetNum) {
    const commit = $('#commit').text();
    const data = {
        table: table,
        commit: commit
    }

    $.ajax({
        type: "POST",
        url: "/get_table_vars", 
        data: JSON.stringify(data, null, '\t'), 
        contentType: 'application/json;charset=UTF-8',
        success: function(data, status) {
            const name = 'colName#' + targetNum;
            const select = $("<select class='col-select' name='" + name + "'>");
            const columns = data.split(" ");
            select.append('<option value="" selected disabled hidden>' + text + '</option>')
            for (var i = 0; i < columns.length; i++) {
                col = columns[i];
                select.append($("<option>").attr('value', col).text(col));
            }
            target.append(select);
        }
    });
}

function showForm(classname, table, sco) {
    const targetNum = classname.replace("target", "");
    const targetClass = $('.' + classname + '-ext');
    console.log('.' + classname + '-ext');
    targetClass.empty();
    switch (sco) {
        case "ADD_COLUMN":
            addTextBox(targetClass, "New column name", targetNum);
            break;
        case "DROP_COLUMN":
            addColumnSelect(targetClass, table, "Column name", targetNum);
            break;
        case "RENAME_COLUMN":
            addColumnSelect(targetClass, table, "Old column name", targetNum);
            addTextBox(targetClass, "New column name", targetNum);
            break;
        case "ADD_TABLE":
            addTextBox(targetClass, "Table name", targetNum);
            break;
        case "DROP_TABLE":
            break;
        case "RENAME_TABLE":
            addTextBox(targetClass, "New table name", targetNum);
            break;
    }
    if (targetClass.css('display') == 'none') {
        targetClass.css("display", "block");
    }
}

function detectFormSelection(classname) {
    console.log(classname);
    return function() {
        allSelected = true;
        let sco = null;
        let table = null;
        $('.' + classname).each(function() {
            if ($(this).val() === '' || $(this).val() === null) {
                allSelected = false;
                return;
            }
            if ($(this).hasClass("sco-select")) sco = $(this).val();
            if ($(this).hasClass("table-select")) table = $(this).val();
        })
        if (allSelected) showForm(classname, table, sco);
    }
}

function addFormListener(classname) {
    $('.' + classname).each(function() {
        $(this).change(detectFormSelection(classname));
    })
}