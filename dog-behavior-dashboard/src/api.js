const API_BASE_URL = 'http://127.0.0.1:8001';

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }
  return await response.json();
};

// Get health status of the API
export const getHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await handleResponse(response);
  } catch (error) {
    console.error('Health check failed:', error);
    throw new Error(`Health check failed: ${error.message}`);
  }
};

// Get model information
export const getModelInfo = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/model/info`);
    return await handleResponse(response);
  } catch (error) {
    console.error('Model info request failed:', error);
    throw new Error(`Model info request failed: ${error.message}`);
  }
};

// Analyze single image
export const analyzeImage = async (file) => {
  try {
    if (!file) {
      throw new Error('No file provided');
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error('File size too large. Please upload an image smaller than 10MB.');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/analyze_image`, {
      method: 'POST',
      body: formData,
    });

    return await handleResponse(response);
  } catch (error) {
    console.error('Image analysis failed:', error);
    throw new Error(`Image analysis failed: ${error.message}`);
  }
};

// Analyze video file
export const analyzeVideo = async (file) => {
  try {
    if (!file) {
      throw new Error('No file provided');
    }

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type. Please upload an MP4, AVI, or MOV video.');
    }

    // Validate file size (max 100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      throw new Error('File size too large. Please upload a video smaller than 100MB.');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/analyze_video`, {
      method: 'POST',
      body: formData,
    });

    return await handleResponse(response);
  } catch (error) {
    console.error('Video analysis failed:', error);
    throw new Error(`Video analysis failed: ${error.message}`);
  }
};

// Analyze live frame (for webcam)
export const analyzeLiveFrame = async (file) => {
  try {
    if (!file) {
      throw new Error('No frame data provided');
    }

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/analyze_live`, {
      method: 'POST',
      body: formData,
    });

    return await handleResponse(response);
  } catch (error) {
    console.error('Live frame analysis failed:', error);
    throw new Error(`Live frame analysis failed: ${error.message}`);
  }
};

// Test API connection
export const testConnection = async () => {
  try {
    await getHealth();
    return { status: 'connected', message: 'API connection successful' };
  } catch (error) {
    return { status: 'error', message: error.message };
  }
};

// Convert base64 to File object for API calls
export const base64ToFile = (base64String, filename = 'frame.jpg', mimeType = 'image/jpeg') => {
  // Remove data URL prefix if present
  const base64Data = base64String.replace(/^data:image\/[a-z]+;base64,/, '');
  
  // Convert base64 to binary
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  
  const byteArray = new Uint8Array(byteNumbers);
  
  return new File([byteArray], filename, { type: mimeType });
};

// Convert canvas to File object
export const canvasToFile = (canvas, filename = 'frame.jpg', quality = 0.8) => {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      const file = new File([blob], filename, { type: 'image/jpeg' });
      resolve(file);
    }, 'image/jpeg', quality);
  });
};
