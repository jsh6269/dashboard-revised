// main.js

function addItem() {
  const title = document.getElementById("title").value;
  const description = document.getElementById("desc").value;

  const formData = new FormData();

  formData.append("title", title);
  formData.append("description", description);

  const fileInput = document.getElementById("image");
  if (fileInput.files.length > 0) {
    formData.append("image", fileInput.files[0]);
  }

  const now = new Date();
  formData.append("created_at", now.toISOString());

  const newItem = Object.fromEntries(formData.entries());
  renderResults([newItem]);
}

function searchItems() {
  const query = document.getElementById("query").value;
  alert(`아직 검색 기능이 구현되지 않았습니다.\nquery=${query}`);
}

function formatDateTime(isoStr) {
  const _datetime = new Date(isoStr);
  if (isNaN(_datetime)) return isoStr;

  const pad = (n) => String(n).padStart(2, "0");

  const year = _datetime.getUTCFullYear();
  const month = _datetime.getUTCMonth();
  const date = _datetime.getUTCDate();
  const hours = _datetime.getUTCHours() + 9;
  const minutes = _datetime.getUTCMinutes();
  const seconds = _datetime.getUTCSeconds();

  // UTC+0 시간을 한국 시간(UTC+9)로 변환하면서 24시를 넘어가는 경우를 보정하기 위해 다시 Date로 감싸기
  const adjustedDate = new Date(
    Date.UTC(year, month, date, hours, minutes, seconds)
  );

  return (
    `${adjustedDate.getUTCFullYear()}-${pad(
      adjustedDate.getUTCMonth() + 1
    )}-${pad(adjustedDate.getUTCDate())} ` +
    `${pad(adjustedDate.getUTCHours())}:${pad(
      adjustedDate.getUTCMinutes()
    )}:${pad(adjustedDate.getUTCSeconds())}`
  );
}

function renderResults(items) {
  const container = document.getElementById("result");
  if (!items || items.length === 0) {
    container.innerHTML = "<p>결과가 없습니다.</p>";
    return;
  }
  container.innerHTML = items
    .map((item) => {
      const imgTag = item.image_path
        ? `<img src="${baseurl}/${item.image_path}" style="max-width:100px;" />`
        : "";
      return `
        <div class="card">
          <h4>${item.title}</h4>
          <p>${item.description || ""}</p>
          ${imgTag}<br/>
          <small style="color:#666;">${
            item.created_at ? formatDateTime(item.created_at) : ""
          }</small>
        </div>
      `;
    })
    .join("");
}
