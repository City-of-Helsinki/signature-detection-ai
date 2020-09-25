import React, { useState } from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import {Paper} from '@material-ui/core';
import {DropzoneArea} from 'material-ui-dropzone';
import { Button } from '@material-ui/core';
import { PictureAsPdf}  from '@material-ui/icons';


function App() {
  const [pdfFiles, setPdfFiles] = useState([]);



  return (
    <Container maxWidth="sm">
      <Paper elevation={3}>
        <Box my={4} p={2} textAlign="center">
          <Typography variant="h4" component="h1" gutterBottom>
            Allekirjoitusten tunnistaja
          </Typography>
          <DropzoneArea
            acceptedFiles={['application/pdf']}
            dropzoneText={'Tipauta PDF tähän tai napsauta kenttää'}
            getDropRejectMessage={(rejectedFile) => {
              return `Sovellus toimii pelkästään PDF-tiedostoilla. Tiedosto ${rejectedFile.name} ei kelpaa.`;
            }}
            Icon={PictureAsPdf}
            showFileNames={true}
            useChipsForPreview={true}
            onChange={(files) => {setPdfFiles(files)}}
          />
          <Box my={2}>
            <Button 
              variant="contained" 
              color="primary"
              onClick={() => {console.log(`There are now ${pdfFiles.length} PDFs`)}}>
                Analysoi
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default App;
