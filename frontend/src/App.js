import React, { useState } from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';
import {Paper} from '@material-ui/core';
import {DropzoneArea} from 'material-ui-dropzone';
import { Button,
         CircularProgress,
         Table,
         TableBody,
         TableCell,
         TableHead,
         TableRow } from '@material-ui/core';
import { PictureAsPdf}  from '@material-ui/icons';


function App() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [view, setView] = useState('input');

  const analyzeFiles = () => {
    const formData = new FormData();
    formData.append('num_files', pdfFiles.length);
    for(const [i, pdfFile] of pdfFiles.entries()) {
      formData.append(pdfFile.name, pdfFile);
    }

    const options = {
      method: 'POST',
      body: formData
    };

    console.log('Sending files for analysis');
    console.log(Array.from(formData.keys()));
    setView('loading');
    fetch('http://localhost:5000/analyze', options)
      .then((response) => response.json())
      .then((data) => {
        console.log('Got response:', data);
        setResults(data.results);
        setView('results');
      })
      .catch((error) => console.log('analyzeFiles() error:', error));
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3}>
        {view === 'input' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
           
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
              maxFileSize={100000000}
              onChange={(files) => {setPdfFiles(files)}}
              showFileNames={true}
              useChipsForPreview={true}
              
            />
            <Box my={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={analyzeFiles}>
                  Analysoi
              </Button>
            </Box>
          </Box>
        : null}

        {view === 'loading' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
            <Typography variant="h4" component="h1" gutterBottom>
              Prosessoidaan...
            </Typography>
            <Box my={12}>
              <CircularProgress />
            </Box>
          </Box>
        : null}

        {view === 'results' ?
          <Box my={4} p={2} textAlign="center" minHeight={400}>
            <Typography variant="h4" component="h1" gutterBottom>
              Tulokset
            </Typography>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tiedosto</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Sivuja</TableCell>
                  <TableCell>Allekirjoituksia sivuilla</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((row) => (
                  <TableRow key={row.filename}>
                    <TableCell component="th" scope="row">
                      {row.filename}
                    </TableCell>
                    <TableCell>{row.status}</TableCell>
                    <TableCell>{row.num_pages}</TableCell>
                    <TableCell>{row.positive.join(", ")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Box my={2}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => setView('input')}>
                  Takaisin
              </Button>
            </Box>
          </Box>
        : null}
      </Paper>
    </Container>
  );
}

export default App;
