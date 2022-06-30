console.log('connected')
function search(){
    var value = document.getElementById('event_search_dropdown').value;

    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("event_search");
    filter = input.value.toUpperCase();
    table = document.getElementById("my_table");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[value];
      if (td) {
        txtValue = td.textContent || td.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
}