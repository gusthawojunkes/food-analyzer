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
const video = document.getElementById("video");

const API = class API {
  static async request(url, body) {
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
};

const FoodController = class FoodController {
  static async searchNutritionalInformation(food) {
    if (!food) {
      throw new Error();
    }

    console.log(`Requesting Nutricional Information for ${food}`);

    try {
      const response = await API.request("/search", {
        query: food,
        pageSize: 1,
      });

      return await response.json();
    } catch (error) {
      return {};
    }
  }

  static async searchByInput() {
    const $input = document.getElementById("search-input");
    const food = $input.value?.trim();
    await FlowController.perform(food);
  }
};

const AlgorithmController = class AlgorithmController {
  static async applyFor(image) {
    console.log(image)

    if (!image?.includes("data:image/png;base64,")) {
      return;
    }

    console.log(`Applying Algorithm`);

    let food = undefined;

    try {
      food = await API.request("/algorithm", { "image": image });
    } catch (error) {
      console.error(error);
    }

    return food;
  }
};

const Content = class Content {
  static startLoading(message = "Carregando...") {
    document.getElementById("overlay").style.display = "flex";
    document.getElementById("loading-message").textContent = message;
  }

  static stopLoading() {
    document.getElementById("overlay").style.display = "none";
  }

  static removeOldContent() {
    document.getElementById("tableContainer").innerHTML = "";
    const $foodNameDiv = document.getElementById("food-main-info-content");
    if ($foodNameDiv) {
      $foodNameDiv.style.display = "none";
      $foodNameDiv.innerHTML = "";
    }
  }

  static addFoodMainInformationToContent(name) {
    const $foodNameDiv = document.getElementById("food-main-info-content");
    if ($foodNameDiv) {
      $foodNameDiv.style.display = "";
      const displayName = name
        ? name[0].toUpperCase() + name.substring(1).toLowerCase()
        : "Sem nome";
      $foodNameDiv.innerHTML = `<strong>${displayName}</strong>`;
    }
  }

  static createNutritionalInformationTableDynamically(nutrients) {
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

  static scrollToNutritionalInformationTable() {
    const targetElement = document.getElementById("tableContainer");
    targetElement.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  static showErrorModal(message = `Ocorreu um erro!`) {
    const $modal = document.getElementById("errorModal");
    const $errorMessageElement = document.getElementById("errorMessage");
    $errorMessageElement.innerHTML = message;
    $modal.style.display = "flex";
    setTimeout(hideErrorModal, 10000);
  }

  static hideErrorModal() {
    const modal = document.getElementById("errorModal");
    modal.style.display = "none";
  }

  static hideNoResultsField() {
    const $div = document.getElementById("empty-table-message");
    if ($div) {
      $div.style.display = "none";
    }
  }
};

const Camera = class Camera {
  static open() {
    if (navigator.mediaDevices?.getUserMedia) {
      const options = { facingMode: "environment" };
      navigator.mediaDevices
        .getUserMedia({ video: options })
        .then((stream) => {
          Camera.playVideo(stream);
        })
        .catch((error) => {
          console.log("Erro ao acessar a câmera!", error);
        });
    }
  }
  static capture() {
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

  static playVideo(stream) {
    if (!video || !stream) throw new Error();
    video.srcObject = stream;
    video.play();
  }

  static async scan() {
    try {
      const image = Camera.capture();
      const food = await AlgorithmController.applyFor(image);

      if (!food || food === "") {
        throw new Error(
          "Nenhum alimento informado, impossível encontrar os dados nutricionais!"
        );
      }
      // await FlowController.perform(
      //   food,
      //   "Aguarde enquanto processamos a sua imagem..."
      // );
    } catch (error) {
      console.error(error);
      if (error.message && error.message !== "") {
        Content.showErrorModal(error.message);
      } else {
        Content.showErrorModal();
      }
    } finally {
      Content.stopLoading();
      Content.hideNoResultsField();
    }
  }
};

const FlowController = class FlowController {
  static async perform(
    food = undefined,
    loadingMessage = "Aguarde enquanto processamos a sua busca..."
  ) {
    try {
      if (!food || food === "") {
        throw new Error(
          "<h3>Nenhum alimento informado!</h3>Impossível encontrar os dados nutricionais"
        );
      }
      Content.startLoading(loadingMessage);
      const nutritionalInformation =
        await FoodController.searchNutritionalInformation(food);
      if (!nutritionalInformation) {
        throw new Error(
          `<h3>Sem dados.</h3>Não foi possível encontrar as informações nutricionais do alimento '${food}'!`
        );
      }
      const nutrients = this.prepareNutritionalInformation(
        nutritionalInformation
      );
      Content.removeOldContent();
      Content.addFoodMainInformationToContent(
        nutritionalInformation.description
      );
      Content.createNutritionalInformationTableDynamically(nutrients);
      Content.scrollToNutritionalInformationTable();
    } catch (error) {
      console.error(error);
      if (error.message && error.message !== "") {
        Content.showErrorModal(error.message);
      } else {
        Content.showErrorModal();
      }
    } finally {
      Content.stopLoading();
      Content.hideNoResultsField();
    }
  }

  static openCamera() {
    Camera.open();
  }

  static prepareNutritionalInformation(nutritionalInformation) {
    return (nutritionalInformation.foodNutrients ?? []).map((nutrient) => {
      return {
        name: nutrient.name,
        amount: `${nutrient.amount}g`,
        quantity: `${nutrient.number}${nutrient.unitName}`.toLocaleLowerCase(),
      };
    });
  }
};

FlowController.openCamera();
