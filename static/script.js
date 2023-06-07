const video = document.getElementById("video");

const labelByKey = {
  brandOwner: "Empresa",
  dataType: "Tipo de dado",
  description: "Descrição",
  fdcId: "ID",
  gtinUpc: "gtinUpc",
  publicationDate: "Data de publicação",
  amount: "Porção",
  name: "Nutriente",
  quantity: "Quantidade",
};

if (navigator.mediaDevices?.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({ video: true, facingMode: "environment" })
    .then(function (stream) {
      video.srcObject = stream;
      video.play();
    })
    .catch(function (error) {
      console.log("Erro ao acessar a câmera: ", error);
    });
}

async function searchByFoodFromInput() {
  const $input = document.getElementById("search-input");
  const food = $input.value?.trim();
  console.log(food);
  await search(food);
}

async function search(
  food = undefined,
  loadingMessage = "Aguarde enquanto processamos a sua busca..."
) {
  try {
    if (!food || food === "") {
      throw new Error(
        "<h3>Nenhum alimento informado!</h3>Impossível encontrar os dados nutricionais"
      );
    }
    startLoading(loadingMessage);
    const nutritionalInformation = await searchNutritionalInformation(food);
    if (!nutritionalInformation) {
      throw new Error(
        `<h3>Sem dados.</h3>Não foi possível encontrar as informações nutricionais do alimento '${food}'!`
      );
    }
    const nutrients = prepareNutritionalInformation(nutritionalInformation);
    removeOldContent();
    addFoodMainInformationToContent(nutritionalInformation.description);
    createNutritionalInformationTableDynamically(nutrients);
    scrollToNutritionalInformationTable();
  } catch (error) {
    console.error(error);
    if (error.message && error.message !== "") {
      showErrorModal(error.message);
    } else {
      showErrorModal();
    }
  } finally {
    stopLoading();
    hideNoResultsField();
  }
}

function hideNoResultsField() {
  const $div = document.getElementById("empty-table-message");
  if ($div) {
    $div.style.display = "none";
  }
}

function captureImage() {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  const width = video.videoWidth;
  const height = video.videoHeight;
  canvas.width = width;
  canvas.height = height;
  context.drawImage(video, 0, 0, width, height);
  const image = canvas.toDataURL("image/png");

  return image;
}

async function scanImage() {
  try {
    const image = captureImage();
    const food = await applyAlgorithm(image);
    if (!food || food === "") {
      throw new Error(
        "Nenhum alimento informado, impossível encontrar os dados nutricionais!"
      );
    }
    await search(food, "Aguarde enquanto processamos a sua imagem...");
  } catch (error) {
    console.error(error);
  } finally {
    stopLoading();
    hideNoResultsField();
  }
}

function scrollToNutritionalInformationTable() {
  const targetElement = document.getElementById("tableContainer");
  targetElement.scrollIntoView({
    behavior: "smooth",
    block: "start",
  });
}

function addFoodMainInformationToContent(name) {
  const $foodNameDiv = document.getElementById("food-main-info-content");
  if ($foodNameDiv) {
    $foodNameDiv.style.display = "";
    const displayName = name
      ? name[0].toUpperCase() + name.substring(1).toLowerCase()
      : "Sem nome";
    $foodNameDiv.innerHTML = `<strong>${displayName}</strong>`;
  }
}

function removeOldContent() {
  document.getElementById("tableContainer").innerHTML = "";
  const $foodNameDiv = document.getElementById("food-main-info-content");
  if ($foodNameDiv) {
    $foodNameDiv.style.display = "none";
    $foodNameDiv.innerHTML = "";
  }
}

function createNutritionalInformationTableDynamically(nutrients) {
  let $tableContainer = document.getElementById("tableContainer");
  let $table = document.createElement("table");
  let $thead = document.createElement("thead");
  let $tbody = document.createElement("tbody");
  let $headerRow = document.createElement("tr");

  let firstNutrient = nutrients[0];
  for (let subKey in firstNutrient) {
    let th = document.createElement("th");
    th.textContent = labelByKey[subKey] ?? subKey;
    $headerRow.appendChild(th);
  }

  $thead.appendChild($headerRow);
  $table.appendChild($thead);

  for (let nutrient of nutrients) {
    let $row = document.createElement("tr");
    for (let subKey in nutrient) {
      let $td = document.createElement("td");
      $td.textContent = nutrient[subKey];
      $row.appendChild($td);
    }
    $tbody.appendChild($row);
  }

  $table.appendChild($tbody);
  $tableContainer.appendChild($table);
}

function startLoading(message = "Carregando...") {
  document.getElementById("overlay").style.display = "flex";
  document.getElementById("loading-message").textContent = message;
}

function stopLoading() {
  document.getElementById("overlay").style.display = "none";
}

function showErrorModal(message = `Ocorreu um erro!`) {
  const $modal = document.getElementById("errorModal");
  const $errorMessageElement = document.getElementById("errorMessage");
  $errorMessageElement.innerHTML = message;
  $modal.style.display = "flex";
  setTimeout(hideErrorModal, 10000);
}

function hideErrorModal() {
  const modal = document.getElementById("errorModal");
  modal.style.display = "none";
}

function prepareNutritionalInformation(nutritionalInformation) {
  return (nutritionalInformation.foodNutrients ?? []).map((nutrient) => {
    return {
      name: nutrient.name,
      amount: nutrient.amount,
      quantity: `${nutrient.number}${nutrient.unitName}`.toLocaleLowerCase(),
    };
  });
}

async function searchNutritionalInformation(food) {
  if (!food) {
    throw new Error();
  }

  console.log(`Requesting Nutricional Information`);

  try {
    const response = await doPost("/search", {
      query: food,
      pageSize: 1,
    });
    let nutritionalInformation = await response.text();
    return JSON.parse(nutritionalInformation)[0];
  } catch (error) {
    return {};
  }
}

async function applyAlgorithm(image) {
  return "Mamão";

  // if (!image?.includes("data:image/png;base64,")) {
  //   return;
  // }

  // console.log(`Applying Algorithm`);

  // let food = undefined;

  // try {
  //   food = await doPost("/algorithm", { image });
  // } catch (error) {
  //   console.error(error);
  // }

  // return food;
}

async function doPost(url, body) {
  console.log(`[API HANDLER] Requesting to: ${url}`);
  let response = undefined;
  try {
    response = await fetch(`/api${url}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
  } catch (error) {
    console.error(error);
  }

  return response;
}
