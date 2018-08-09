document.addEventListener('DOMContentLoaded', () =>
{

     // Adding Team members to the Project
     $('#addTeam').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget); // Button that triggered the modal
      var recipient = button.data('projname'); // Extract info from data-* attributes
      var modal = $(this);
      modal.find('.modal-title').text(`Project:${recipient}`);

      var MembersArea = document.querySelector('#MembersArea');
      var MembersAreaChild = document.querySelector('#MembersAreaChild');
      if (MembersAreaChild)
       {
          MembersAreaChild.remove() ;
       }
       MembersAreaChild = document.createElement("div");
       MembersAreaChild.setAttribute("id","MembersAreaChild");
       MembersArea.appendChild(MembersAreaChild);
       //MembersArea.innerHTML='<strong>Available list of members to select from:</strong>';

       var userlist =  button.data('allusers');
       console.log(userlist)
      for(var idx =0; idx < userlist.length; idx++)
              {
                console.log(userlist[idx][2]);
                var seperator = document.createElement('div');
                var checkbox = document.createElement('input');
                var label = document.createElement('label');
                checkbox.type = "checkbox";
                checkbox.name = "tmember";
                checkbox.className = "c_tmember";
                checkbox.value = userlist[idx][0];
                checkbox.id = userlist[idx][0];
                label.htmlFor = userlist[idx][0];
                label.innerText = userlist[idx][2];
                console.log(label);
                console.log(checkbox);
                seperator.appendChild(checkbox);
                seperator.appendChild(label);
                console.log(seperator)
                MembersAreaChild.appendChild(seperator);
              }
    });


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

    // Each Task edit button change it to edit mode
    document.querySelectorAll('.task_edit_cancel_btn').forEach(button => {
      button.onclick = () => {
          const taskid = button.dataset.taskid;
          var ro_element = document.querySelector(`#task_ro_${taskid}`);
          var edit_element = document.querySelector(`#task_edit_${taskid}`);
          if (ro_element) ro_element.style.display = "block";
          if (edit_element) edit_element.style.display = "none";

          };
      });

    // Each Task remove button
    document.querySelectorAll('.task_remove_btn').forEach(button => {
      button.onclick = () => {
          console.log('Inside button delete');
          const taskid = button.dataset.taskid;
          const title = button.dataset.title;
          var ro_element = document.querySelector(`#task_ro_${taskid}`);
          var edit_element = document.querySelector(`#task_edit_${taskid}`);

          if (ro_element)
          {
            ro_element.style.animationPlayState = 'running';
            ro_element.addEventListener('animationend', () =>  {
                        ro_element.remove();
                    });
          }
          if (edit_element) edit_element.remove();

          // POST the taskID to remove
          // Initialize new request
          const request = new XMLHttpRequest();

          request.open('POST', '/deletetask');
          var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  		    request.setRequestHeader("X-CSRFToken", csrftoken);

          // Callback function for when request completes
          request.onload = () => {
              // Extract JSON data from request
              const data = JSON.parse(request.responseText);
              var msg_element = document.querySelector('#pg_msg_area');
              // Display response on the pageMessageArea
              if (data.success) {
                  if (msg_element)
                    msg_element.innerHTML=`<div class="alert alert-success" role="alert"> ${data.message} </div>`;
                    }
              else {
                  if (msg_element) msg_element.innerHTML=`<div class="alert alert-success" role="alert"> ${data.message}</div>`;
                  console.log(data.message);
                }
            }

          // Add data to send with request
          const data = new FormData();
          data.append('taskid', taskid);
          data.append('title', title);

          // Send request
          request.send(data);
          return false;
          };
      });


  // reference to a list
  const taskrow = document.querySelector('.row_buckets');
  // add a single listener on list item
  taskrow.addEventListener('click', clickHandler);

} // function of DOMContentLoaded
);


// Each Task Move link
function clickHandler(e)
{
  //console.log(e.target.innerHTML);
  if (e.target.matches('.move_task_link')) {
    move_task_link(e.target);
  }
}

function move_task_link(link)
 {
    console.log('Inside move_task_link');

    var linkparent = link.parentNode.parentNode;
    console.log(link);
    console.log(linkparent);

    const taskid = link.dataset.taskid;
    const title = link.dataset.title;
    const dest_bucketid = link.dataset.bucketid;
    const dest_bucketname = link.dataset.bucketname;
    const curr_bucketid = linkparent.dataset.currbucketid;
    const curr_bucketname = linkparent.dataset.currbucketname;

    console.log(`curr_bucketname:${curr_bucketname}`);
    console.log(`dest_bucketname:${dest_bucketname}`);

    // change the values on link
    linkparent.setAttribute('data-currbucketid', dest_bucketid);
    linkparent.setAttribute('data-currbucketname', dest_bucketname);
    link.setAttribute('data-bucketid', curr_bucketid);
    link.setAttribute('data-bucketname', curr_bucketname);
    link.innerHTML = curr_bucketname;

    var move_whole_task = document.querySelector(`#move_whole_task_${taskid}`);
    var clone_whole_task = move_whole_task.cloneNode(true);

    // get destination bucket
    var dest_bucket = document.querySelector(`#bucketBody_${dest_bucketid}`);

    if (move_whole_task) move_whole_task.remove();
    if (dest_bucket) dest_bucket.appendChild(clone_whole_task);

    ////////////////////////////////////////
              // Initialize new request
          const request = new XMLHttpRequest();

          request.open('POST', '/movetask');
          var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
  		    request.setRequestHeader("X-CSRFToken", csrftoken);

          // Callback function for when request completes
          request.onload = () => {
              // Extract JSON data from request
              const data = JSON.parse(request.responseText);
              var msg_element = document.querySelector('#pg_msg_area');
              // Display response on the pageMessageArea
              if (data.success) {
                  if (msg_element)
                    msg_element.innerHTML=`<div class="alert alert-success" role="alert"> ${data.message} </div>`;
                    }
              else {
                  if (msg_element) msg_element.innerHTML=`<div class="alert alert-success" role="alert"> ${data.message}</div>`;
                  console.log(data.message);
                }
            }

          // Add data to send with request
          const data = new FormData();
          data.append('taskid', taskid);
          data.append('dest_bucketid',dest_bucketid);
          data.append('dest_bucketname',dest_bucketname);
          data.append('title', title);

          // Send request
          request.send(data);
          return false;
    ////////////////////////////////////////
  }