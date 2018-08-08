document.addEventListener('DOMContentLoaded', () =>
{

    // Template for new Task
    const new_task_template = Handlebars.compile(document.querySelector('#new_task_template').innerHTML);

    // Each save button display values in console
    document.querySelectorAll('.add_task_bttn').forEach(button => {
      button.onclick = () => {
          const bucketid = button.dataset.bucketid;
          var teammembers =button.dataset.teammembers;
          console.log(teammembers);
          console.log(JSON.parse(teammembers).length);

          var val = {'projectid':button.dataset.projectid,
                 'bucketid':button.dataset.bucketid,
                 'teammembers':JSON.parse(teammembers)
          }

          const content = new_task_template(val);
          document.querySelector(`#new_task_form_${bucketid}`).innerHTML += content;

          };
      });

    // Each Task edit button change it to edit mode
    document.querySelectorAll('.task_edit_btn').forEach(button => {
      button.onclick = () => {
          const taskid = button.dataset.taskid;
          var ro_element = document.querySelector(`#task_ro_${taskid}`);
          var edit_element = document.querySelector(`#task_edit_${taskid}`);
          if (ro_element) ro_element.style.display = "none";
          if (edit_element) edit_element.style.display = "block";

          };
      });


} // function of DOMContentLoaded
);